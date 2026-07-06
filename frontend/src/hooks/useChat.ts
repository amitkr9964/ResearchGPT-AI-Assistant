import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatApi } from '../services/api';

export function useChatHistory() {
  return useQuery({
    queryKey: ['chatHistory'],
    queryFn: async () => {
      const res = await chatApi.getHistory();
      return res.data;
    },
  });
}

export function useConversation(id: number | null) {
  return useQuery({
    queryKey: ['conversation', id],
    queryFn: async () => {
      if (!id) return null;
      const res = await chatApi.getConversation(id);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => chatApi.deleteConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    },
  });
}
