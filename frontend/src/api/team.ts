import { request } from './request';

export type TeamRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface Team {
  teamId: string;
  name: string;
  description?: string;
  ownerId: string;
  settings: {
    allowMemberInvite: boolean;
    defaultRole: TeamRole;
  };
  createdAt: string;
  updatedAt: string;
}

export interface TeamMember {
  id: string;
  teamId: string;
  userId: string;
  role: TeamRole;
  permissions: Record<string, boolean>;
  joinedAt: string;
  userName?: string;
  userEmail?: string;
}

export interface RolePermissions {
  canManageTeam: boolean;
  canInviteMember: boolean;
  canRemoveMember: boolean;
  canManageProject: boolean;
  canEditDocument: boolean;
  canViewDocument: boolean;
  canDeleteProject: boolean;
}

export function getMyTeams() {
  return request.get<unknown, Team[]>('/v1/teams/my');
}

export function getTeamDetail(teamId: string) {
  return request.get<unknown, Team & { members: TeamMember[] }>(`/v1/teams/${teamId}`);
}

export function createTeam(data: { name: string; description?: string }) {
  return request.post<unknown, Team>('/v1/teams', data);
}

export function updateTeam(teamId: string, data: Partial<Team>) {
  return request.put<unknown, Team>(`/v1/teams/${teamId}`, data);
}

export function deleteTeam(teamId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}`);
}

export function inviteTeamMember(teamId: string, data: { email: string; role?: TeamRole }) {
  return request.post<unknown, TeamMember>(`/v1/teams/${teamId}/members`, data);
}

export function updateMemberRole(teamId: string, userId: string, role: TeamRole) {
  return request.put<unknown, TeamMember>(`/v1/teams/${teamId}/members/${userId}/role`, {
    role,
  });
}

export function removeTeamMember(teamId: string, userId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}/members/${userId}`);
}

export function getMyPermissions(teamId: string) {
  return request.get<unknown, RolePermissions>(`/v1/teams/${teamId}/my-permissions`);
}

export function assignProjectToTeam(projectId: string, teamId: string) {
  return request.post<unknown, { message: string }>(`/v1/teams/${teamId}/projects`, {
    project_id: projectId,
  });
}

export function removeProjectFromTeam(teamId: string, projectId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}/projects/${projectId}`);
}
