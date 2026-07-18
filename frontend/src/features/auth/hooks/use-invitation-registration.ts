import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { invitationService } from "@/services/invitation.service";
import type { RegisterUserDTO } from "@/types/dto/invitation.dto";

export function useValidateInvitation(token: string) {
  return useQuery({
    queryKey: ["invitation", token],
    queryFn: () => invitationService.validateInvitation(token),
    enabled: Boolean(token),
    retry: 1,
  });
}

export function useRegisterUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegisterUserDTO) => invitationService.registerUser(data),
    onSuccess: (_, variables) => {
      queryClient.removeQueries({ queryKey: ["invitation", variables.token] });
    },
    retry: 1,
  });
}
