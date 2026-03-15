import PropTypes from 'prop-types'
import styles from './InstrumentTable.module.css'

/**
 * Renders a table of instruments with edit/delete actions per row.
 * Clicking a row (outside action buttons) calls onRowClick with the instrument id.
 */
export default function InstrumentTable({ instruments, onEdit, onDelete, onRowClick }) {
  if (instruments.length === 0) {
    return <p className={styles.empty}>No instruments found.</p>
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Name</th>
          <th>Asset Type</th>
          <th>Active</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {instruments.map((inst) => (
          <tr
            key={inst.id}
            className={styles.row}
            onClick={() => onRowClick(inst.id)}
            style={{ cursor: 'pointer' }}
          >
            <td>{inst.symbol}</td>
            <td>{inst.name}</td>
            <td>{inst.asset_type}</td>
            <td>{inst.is_active ? 'Yes' : 'No'}</td>
            <td>
              <button
                className={styles.actionBtn}
                onClick={(e) => {
                  e.stopPropagation()
                  onEdit(inst)
                }}
                aria-label={`Edit ${inst.symbol}`}
              >
                Edit
              </button>
              <button
                className={`${styles.actionBtn} ${styles.danger}`}
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(inst.id)
                }}
                aria-label={`Delete ${inst.symbol}`}
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

InstrumentTable.propTypes = {
  /** Array of instrument objects to display */
  instruments: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      symbol: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      asset_type: PropTypes.string.isRequired,
      is_active: PropTypes.bool.isRequired,
    })
  ).isRequired,
  /** Called with the full instrument object when Edit is clicked */
  onEdit: PropTypes.func.isRequired,
  /** Called with the instrument id when Delete is clicked */
  onDelete: PropTypes.func.isRequired,
  /** Called with the instrument id when a row is clicked */
  onRowClick: PropTypes.func.isRequired,
}
