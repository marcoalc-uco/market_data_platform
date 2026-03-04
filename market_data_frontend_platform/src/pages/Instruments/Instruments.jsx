import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInstruments } from '../../hooks/useInstruments.js'
import { useInstrumentMutations } from '../../hooks/useInstrumentMutations.js'
import InstrumentTable from '../../components/InstrumentTable/InstrumentTable.jsx'
import InstrumentFilters from '../../components/InstrumentFilters/InstrumentFilters.jsx'
import InstrumentForm from '../../components/InstrumentForm/InstrumentForm.jsx'
import Pagination from '../../components/Pagination/Pagination.jsx'
import styles from './Instruments.module.css'

const DEFAULT_LIMIT = 20

export default function Instruments() {
  const navigate = useNavigate()

  const [filters, setFilters] = useState({ asset_type: undefined, is_active: undefined })
  const [pagination, setPagination] = useState({ skip: 0, limit: DEFAULT_LIMIT })
  const [form, setForm] = useState({ open: false, instrument: null })

  // Build query params — strip undefined/empty values before sending to the API
  const queryParams = Object.fromEntries(
    Object.entries({ ...filters, ...pagination }).filter(([, v]) => v !== undefined && v !== '')
  )

  const { data: instruments = [], isLoading, error, refetch } = useInstruments(queryParams)
  const { create, update, remove } = useInstrumentMutations()

  const activeMutation = form.instrument ? update : create

  const openCreate = () => setForm({ open: true, instrument: null })
  const openEdit = (instrument) => setForm({ open: true, instrument })
  const closeForm = () => {
    create.reset()
    update.reset()
    setForm({ open: false, instrument: null })
  }

  const handleFormSubmit = (data) => {
    if (form.instrument) {
      update.mutate({ id: form.instrument.id, data }, { onSuccess: closeForm })
    } else {
      create.mutate(data, { onSuccess: closeForm })
    }
  }

  const handleDelete = (id) => {
    if (window.confirm('Delete this instrument?')) {
      remove.mutate(id)
    }
  }

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters)
    setPagination((prev) => ({ ...prev, skip: 0 }))
  }

  if (isLoading) {
    return <p className={styles.status}>Loading instruments…</p>
  }

  if (error) {
    return (
      <div className={styles.status}>
        <p role="alert">Error: {error.message}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Instruments</h1>
        <button onClick={openCreate}>+ Add Instrument</button>
      </header>

      <InstrumentFilters filters={filters} onChange={handleFiltersChange} />

      <InstrumentTable
        instruments={instruments}
        onEdit={openEdit}
        onDelete={handleDelete}
        onRowClick={(id) => navigate(`/instruments/${id}/prices`)}
      />

      <Pagination
        skip={pagination.skip}
        limit={pagination.limit}
        hasMore={instruments.length === pagination.limit}
        onChange={setPagination}
      />

      {form.open && (
        <InstrumentForm
          instrument={form.instrument}
          onSubmit={handleFormSubmit}
          onClose={closeForm}
          isLoading={activeMutation.isPending}
          error={activeMutation.error}
        />
      )}
    </div>
  )
}
