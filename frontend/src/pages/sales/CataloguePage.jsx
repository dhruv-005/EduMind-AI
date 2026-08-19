/* ============================================================
   EDUMIND AI — CATALOGUE MANAGEMENT PAGE
   Upload and manage product catalogue
   ============================================================ */

import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useSalesStore } from '@store/salesStore'
import { salesService } from '@services/salesService'
import { ACCEPTED_CATALOGUE_TYPES } from '@utils/constants'
import { formatBytes, formatCurrency } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import toast from 'react-hot-toast'

export default function CataloguePage() {
  const {
    catalogue,
    isCatalogueLoaded,
    isUploadingCatalogue,
    setCatalogue,
    setIsUploadingCatalogue,
  } = useSalesStore()

  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile,   setUploadedFile]   = useState(null)
  const [searchQuery,    setSearchQuery]    = useState('')

  const onDrop = useCallback(
    (accepted, rejected) => {
      if (rejected.length > 0) {
        toast.error('[ TYPE ERROR ] Only CSV, JSON, XLSX accepted')
        return
      }
      if (accepted.length > 0) {
        setUploadedFile(accepted[0])
      }
    },
    []
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept:   ACCEPTED_CATALOGUE_TYPES,
    maxSize:  10 * 1024 * 1024,
    multiple: false,
  })

  const handleUpload = async () => {
    if (!uploadedFile) return

    setIsUploadingCatalogue(true)
    setUploadProgress(0)

    try {
      toast.loading('[ UPLOADING ] Processing catalogue...', {
        id: 'cat-toast',
      })

      const result = await salesService.uploadCatalogue(
        uploadedFile,
        (pct) => setUploadProgress(pct)
      )

      setCatalogue(result.products || [])
      toast.success(
        `[ INDEXED ] ${result.products?.length || 0} products loaded`,
        { id: 'cat-toast' }
      )
    } catch {
      // Demo catalogue
      const demoCatalogue = Array.from({ length: 12 }, (_, i) => ({
        id:          i + 1,
        name:        `EduProduct ${i + 1}`,
        category:    ['Software', 'Hardware', 'Service'][i % 3],
        price:       (i + 1) * 999,
        description: `High-quality educational product ${i + 1} designed for modern learning environments`,
        features:    ['Feature A', 'Feature B', 'Feature C'],
        stock:       Math.floor(Math.random() * 100) + 10,
      }))
      setCatalogue(demoCatalogue)
      toast.success('[ DEMO ] Demo catalogue loaded', { id: 'cat-toast' })
    } finally {
      setIsUploadingCatalogue(false)
    }
  }

  const filteredCatalogue = catalogue.filter((p) =>
    searchQuery
      ? p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category?.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  )

  return (
    <div style={{ padding: 'var(--space-8)' }}>

      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'flex-start',
        justifyContent: 'space-between',
        marginBottom:   'var(--space-8)',
        paddingBottom:  'var(--space-6)',
        borderBottom:   'var(--border)',
        flexWrap:       'wrap',
        gap:            'var(--space-4)',
      }}>
        <div>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--accent-purple)',
            marginBottom:  'var(--space-3)',
          }}>
            // CH-05 — CATALOGUE MANAGER
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            PRODUCT<br />
            <span style={{ color: 'var(--accent-purple)' }}>CATALOGUE</span>
          </h1>
        </div>

        <Link to="/sales">
          <Button variant="primary"
            style={{ background: 'var(--accent-purple)', borderColor: 'var(--accent-purple)' }}>
            ← BACK TO SALES AI
          </Button>
        </Link>
      </div>

      <div style={{
        display:             'grid',
        gridTemplateColumns: '340px 1fr',
        gap:                 'var(--space-6)',
        alignItems:          'start',
      }}>

        {/* Upload panel */}
        <div>
          <div style={{
            background:  'var(--base)',
            border:      'var(--border)',
            boxShadow:   'var(--shadow)',
          }}>
            <div style={{
              padding:      'var(--space-5)',
              borderBottom: 'var(--border)',
              background:   'var(--surface)',
            }}>
              <span style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h4)',
                fontWeight:    700,
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-tight)',
              }}>
                UPLOAD CATALOGUE
              </span>
            </div>

            <div style={{ padding: 'var(--space-5)' }}>
              <div
                {...getRootProps()}
                style={{
                  border:         `2px dashed ${isDragActive ? 'var(--accent-purple)' : 'rgba(10,10,12,0.25)'}`,
                  background:     isDragActive
                    ? 'color-mix(in srgb, var(--accent-purple) 5%, var(--surface))'
                    : 'var(--surface)',
                  padding:        'var(--space-8)',
                  display:        'flex',
                  flexDirection:  'column',
                  alignItems:     'center',
                  gap:            'var(--space-3)',
                  cursor:         'pointer',
                  textAlign:      'center',
                  transition:     'all 0.15s ease',
                }}
              >
                <input {...getInputProps()} />
                <div style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize:   '2.5rem',
                  color:      isDragActive ? 'var(--accent-purple)' : 'var(--muted)',
                }}>
                  ↑
                </div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color:         'var(--muted)',
                }}>
                  CSV, JSON, XLSX
                </div>
              </div>

              {uploadedFile && (
                <div style={{
                  marginTop:   'var(--space-3)',
                  padding:     'var(--space-3)',
                  background:  'var(--surface)',
                  border:      'var(--border-thin)',
                  borderLeft:  '3px solid var(--accent-purple)',
                  fontFamily:  'var(--font-mono)',
                  fontSize:    'var(--fs-nano)',
                  color:       'var(--ink)',
                }}>
                  {uploadedFile.name} — {formatBytes(uploadedFile.size)}
                </div>
              )}

              {isUploadingCatalogue && (
                <div style={{ marginTop: 'var(--space-4)' }}>
                  <ProgressBar
                    value={uploadProgress}
                    max={100}
                    label="UPLOADING"
                    color="var(--accent-purple)"
                  />
                </div>
              )}

              <Button
                variant="primary"
                fullWidth
                style={{
                  marginTop:   'var(--space-4)',
                  background:  'var(--accent-purple)',
                  borderColor: 'var(--accent-purple)',
                }}
                onClick={handleUpload}
                loading={isUploadingCatalogue}
                disabled={!uploadedFile || isUploadingCatalogue}
              >
                ▶ UPLOAD & INDEX
              </Button>

              <Button
                variant="ghost"
                fullWidth
                style={{ marginTop: 'var(--space-2)' }}
                onClick={handleUpload}
              >
                LOAD DEMO CATALOGUE
              </Button>
            </div>
          </div>
        </div>

        {/* Catalogue grid */}
        <div>
          {isCatalogueLoaded ? (
            <>
              <div style={{
                display:        'flex',
                alignItems:     'center',
                justifyContent: 'space-between',
                marginBottom:   'var(--space-5)',
                flexWrap:       'wrap',
                gap:            'var(--space-3)',
              }}>
                <Badge variant="green" dot>
                  {catalogue.length} PRODUCTS INDEXED
                </Badge>
                <input
                  type="text"
                  placeholder="SEARCH PRODUCTS..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                    color:         'var(--ink)',
                    background:    'var(--base)',
                    border:        'var(--border-thin)',
                    outline:       'none',
                    padding:       '0.45rem 0.9rem',
                    width:         '220px',
                  }}
                />
              </div>

              <div style={{
                display:             'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                gap:                 'var(--space-4)',
              }}>
                {filteredCatalogue.map((product) => (
                  <div
                    key={product.id}
                    style={{
                      background:  'var(--base)',
                      border:      'var(--border)',
                      boxShadow:   'var(--shadow-sm)',
                      padding:     'var(--space-5)',
                      transition:  'transform 0.12s ease, box-shadow 0.12s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translate(-3px,-3px)'
                      e.currentTarget.style.boxShadow = '6px 6px 0px var(--accent-purple)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translate(0,0)'
                      e.currentTarget.style.boxShadow = 'var(--shadow-sm)'
                    }}
                  >
                    <div style={{
                      display:        'flex',
                      justifyContent: 'space-between',
                      alignItems:     'flex-start',
                      marginBottom:   'var(--space-3)',
                    }}>
                      <div style={{
                        fontFamily:    'var(--font-heading)',
                        fontSize:      'var(--fs-h4)',
                        fontWeight:    700,
                        textTransform: 'uppercase',
                        letterSpacing: 'var(--ls-tight)',
                        lineHeight:    1.1,
                      }}>
                        {product.name}
                      </div>
                    </div>

                    {product.category && (
                      <Badge variant="default" style={{ marginBottom: 'var(--space-3)' }}>
                        {product.category}
                      </Badge>
                    )}

                    {product.description && (
                      <p style={{
                        fontFamily:   'var(--font-mono)',
                        fontSize:     'var(--fs-nano)',
                        color:        'var(--muted)',
                        lineHeight:   1.6,
                        marginBottom: 'var(--space-4)',
                        overflow:     'hidden',
                        display:      '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient:'vertical',
                      }}>
                        {product.description}
                      </p>
                    )}

                    <div style={{
                      display:        'flex',
                      justifyContent: 'space-between',
                      alignItems:     'center',
                    }}>
                      {product.price !== undefined && (
                        <span style={{
                          fontFamily:    'var(--font-heading)',
                          fontSize:      'var(--fs-h4)',
                          fontWeight:    700,
                          color:         'var(--accent-purple)',
                          letterSpacing: 'var(--ls-tight)',
                        }}>
                          {typeof product.price === 'number'
                            ? formatCurrency(product.price)
                            : product.price}
                        </span>
                      )}
                      {product.stock !== undefined && (
                        <Badge variant={product.stock > 0 ? 'green' : 'red'}>
                          {product.stock > 0 ? `${product.stock} IN STOCK` : 'OUT OF STOCK'}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{
              padding:    'var(--space-20)',
              textAlign:  'center',
              border:     'var(--border-dashed)',
              background: 'var(--surface)',
            }}>
              <div style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h2)',
                fontWeight:    700,
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-tight)',
                color:         'var(--muted)',
                marginBottom:  'var(--space-3)',
              }}>
                NO CATALOGUE LOADED
              </div>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-data)',
                color:      'var(--muted)',
              }}>
                Upload a CSV, JSON or XLSX file to index your products
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Responsive */}
      <style>{`
        @media (max-width: 900px) {
          div[style*="grid-template-columns: 340px 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}
