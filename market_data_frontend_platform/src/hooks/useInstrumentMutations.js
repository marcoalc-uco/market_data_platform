import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createInstrument, updateInstrument, deleteInstrument } from '../api/instruments.js'

/**
 * Returns TanStack Query mutations for creating, updating and deleting
 * instruments. Each mutation invalidates the ['instruments'] query on success.
 */
export function useInstrumentMutations() {
  const queryClient = useQueryClient()

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['instruments'] })

  const create = useMutation({
    mutationFn: createInstrument,
    onSuccess: invalidate,
  })

  const update = useMutation({
    mutationFn: ({ id, data }) => updateInstrument(id, data),
    onSuccess: invalidate,
  })

  const remove = useMutation({
    mutationFn: deleteInstrument,
    onSuccess: invalidate,
  })

  return { create, update, remove }
}
