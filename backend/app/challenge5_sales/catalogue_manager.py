import uuid
import json
import csv
import io
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.logger import logger
from app.core.exceptions import FileProcessingException
from app.shared.embeddings import embedding_service
from app.shared.vector_store import (
    vector_store,
    COLLECTION_PRODUCTS
)


class CatalogueManager:
    """
    Manage product catalogue upload and indexing.
    Supports CSV, JSON, Excel formats.
    Indexes products in ChromaDB for semantic search.
    """

    def parse_csv(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Parse CSV product catalogue."""
        products = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    product = self._normalize_product(
                        dict(row)
                    )
                    if product.get("name"):
                        products.append(product)

            logger.info(
                f"Parsed {len(products)} products from CSV"
            )
            return products

        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            raise FileProcessingException(
                f"Failed to parse CSV: {str(e)}"
            )

    def parse_json(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Parse JSON product catalogue."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                raw_products = data
            elif isinstance(data, dict):
                raw_products = data.get(
                    "products",
                    data.get("items", [data])
                )
            else:
                raw_products = []

            products = [
                self._normalize_product(p)
                for p in raw_products
                if isinstance(p, dict) and p.get("name")
            ]

            logger.info(
                f"Parsed {len(products)} products from JSON"
            )
            return products

        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            raise FileProcessingException(
                f"Failed to parse JSON: {str(e)}"
            )

    def parse_excel(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Parse Excel product catalogue."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            headers = []
            products = []

            for row_idx, row in enumerate(ws.iter_rows()):
                values = [
                    cell.value for cell in row
                ]

                if row_idx == 0:
                    headers = [
                        str(v).lower().strip()
                        if v else f"col_{i}"
                        for i, v in enumerate(values)
                    ]
                else:
                    if any(v is not None for v in values):
                        product_dict = dict(
                            zip(headers, values)
                        )
                        product = self._normalize_product(
                            product_dict
                        )
                        if product.get("name"):
                            products.append(product)

            logger.info(
                f"Parsed {len(products)} products from Excel"
            )
            return products

        except ImportError:
            logger.warning(
                "openpyxl not installed. "
                "Run: pip install openpyxl"
            )
            raise FileProcessingException(
                "openpyxl not installed for Excel parsing"
            )
        except Exception as e:
            raise FileProcessingException(
                f"Failed to parse Excel: {str(e)}"
            )

    def _normalize_product(
        self,
        raw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Normalize product dict to standard format.
        Handles various column naming conventions.
        """
        def get_field(keys: List[str]) -> Any:
            for key in keys:
                for raw_key in raw:
                    if raw_key.lower().strip() == key:
                        val = raw[raw_key]
                        if val is not None and str(val).strip():
                            return val
            return None

        name = get_field([
            "name", "product_name", "title", "product"
        ])
        if not name:
            return {}

        price_raw = get_field([
            "price", "cost", "amount", "regular_price"
        ])
        try:
            price = float(
                str(price_raw).replace(
                    "$", ""
                ).replace(",", "")
            ) if price_raw else 0.0
        except ValueError:
            price = 0.0

        features_raw = get_field([
            "features", "specifications", "specs"
        ])
        features = []
        if features_raw:
            if isinstance(features_raw, list):
                features = features_raw
            elif isinstance(features_raw, str):
                features = [
                    f.strip()
                    for f in features_raw.split(",")
                    if f.strip()
                ]

        category = get_field([
            "category", "type", "product_type",
            "department"
        ])
        brand = get_field(["brand", "manufacturer", "make"])
        description = get_field([
            "description", "short_description",
            "details", "about"
        ])
        sku = get_field(["sku", "id", "product_id", "code"])
        in_stock_raw = get_field([
            "in_stock", "available", "stock",
            "availability"
        ])
        in_stock = True
        if in_stock_raw is not None:
            if isinstance(in_stock_raw, bool):
                in_stock = in_stock_raw
            else:
                in_stock = str(
                    in_stock_raw
                ).lower() not in [
                    "false", "0", "no", "out of stock"
                ]

        rating_raw = get_field([
            "rating", "score", "stars"
        ])
        try:
            rating = float(rating_raw) if rating_raw else None
        except (ValueError, TypeError):
            rating = None

        return {
            "id": str(uuid.uuid4()),
            "name": str(name).strip(),
            "brand": str(brand).strip() if brand else None,
            "category": str(
                category
            ).strip() if category else None,
            "sku": str(sku).strip() if sku else None,
            "price": price,
            "currency": "USD",
            "short_description": str(
                description
            ).strip() if description else None,
            "features": features,
            "in_stock": in_stock,
            "rating": rating,
            "final_price": price,
            "specifications": {},
            "target_audience": None,
            "use_cases": [],
            "image_url": get_field([
                "image", "image_url", "photo"
            ]),
            "product_url": get_field([
                "url", "link", "product_url"
            ])
        }

    def build_embedding_text(
        self,
        product: Dict[str, Any]
    ) -> str:
        """Build text for vector embedding."""
        parts = [
            product.get("name", ""),
            product.get("brand", "") or "",
            product.get("category", "") or "",
            product.get("short_description", "") or "",
            " ".join(product.get("features", [])),
            f"price {product.get('price', 0)}",
            "in stock" if product.get("in_stock") else "out of stock"
        ]
        return " ".join(filter(None, parts))

    async def index_products(
        self,
        products: List[Dict[str, Any]],
        catalogue_id: str
    ) -> int:
        """
        Index products in ChromaDB vector store.
        Returns number of products indexed.
        """
        if not products:
            return 0

        # Build texts for embedding
        texts = [
            self.build_embedding_text(p)
            for p in products
        ]

        # Generate embeddings in batches
        batch_size = 50
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = embedding_service.embed_texts(batch)
            all_embeddings.extend(embeddings)

        # Filter out products with failed embeddings
        valid_products = []
        valid_embeddings = []
        valid_ids = []
        valid_texts = []
        valid_metadatas = []

        for product, embedding, text in zip(
            products, all_embeddings, texts
        ):
            if embedding:
                valid_products.append(product)
                valid_embeddings.append(embedding)
                valid_ids.append(product["id"])
                valid_texts.append(text)
                valid_metadatas.append({
                    "catalogue_id": catalogue_id,
                    "name": product["name"],
                    "brand": product.get("brand", ""),
                    "category": product.get("category", ""),
                    "price": str(product.get("price", 0)),
                    "in_stock": str(
                        product.get("in_stock", True)
                    )
                })

        # Add to ChromaDB
        success = vector_store.upsert_documents(
            collection_name=COLLECTION_PRODUCTS,
            documents=valid_texts,
            embeddings=valid_embeddings,
            ids=valid_ids,
            metadatas=valid_metadatas
        )

        indexed = len(valid_products) if success else 0
        logger.info(
            f"Indexed {indexed}/{len(products)} products "
            f"in ChromaDB"
        )

        return indexed

    async def process_catalogue_file(
        self,
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Process uploaded catalogue file.
        Parse, normalize, and index products.
        """
        catalogue_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower()

        # Parse based on file type
        if ext == ".csv":
            products = self.parse_csv(file_path)
        elif ext == ".json":
            products = self.parse_json(file_path)
        elif ext in [".xlsx", ".xls"]:
            products = self.parse_excel(file_path)
        else:
            raise FileProcessingException(
                f"Unsupported file format: {ext}"
            )

        if not products:
            raise FileProcessingException(
                "No valid products found in file"
            )

        # Index in ChromaDB
        indexed_count = await self.index_products(
            products=products,
            catalogue_id=catalogue_id
        )

        # Get unique categories
        categories = list(set(
            p.get("category", "")
            for p in products
            if p.get("category")
        ))

        return {
            "catalogue_id": catalogue_id,
            "total_products": len(products),
            "indexed_products": indexed_count,
            "categories": categories,
            "products": products,
            "message": (
                f"Successfully indexed "
                f"{indexed_count} products"
            )
        }

    async def search_products(
        self,
        query: str,
        budget_max: Optional[float] = None,
        category: Optional[str] = None,
        in_stock_only: bool = True,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search products using semantic search.
        Applies filters after semantic search.
        """
        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)

        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []

        # Build ChromaDB filter
        where_filter = None
        if in_stock_only:
            where_filter = {"in_stock": "True"}

        # Semantic search
        results = vector_store.search(
            collection_name=COLLECTION_PRODUCTS,
            query_embedding=query_embedding,
            top_k=top_k * 2,
            where=where_filter
        )

        # Apply price filter
        if budget_max is not None:
            results = [
                r for r in results
                if float(
                    r.get("metadata", {}).get("price", 0)
                ) <= budget_max
            ]

        # Apply category filter
        if category:
            cat_lower = category.lower()
            results = [
                r for r in results
                if cat_lower in r.get(
                    "metadata", {}
                ).get("category", "").lower()
            ]

        return results[:top_k]


# Singleton
catalogue_manager = CatalogueManager()
