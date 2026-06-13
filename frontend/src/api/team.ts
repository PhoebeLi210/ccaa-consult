import { request } from './request';

export type TeamRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface Team {
  team_id: string;
  name: string;
  description?: string;
  owner_id: string;
  settings: {
    allow_member_invite: boolean;
    default_role: TeamRole;
  };
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  role: TeamRole;
  permissions: Record<string, boolean>;
  joined_at: string;
  user_name?: string;
  user_email?: string;
}

export interface RolePermissions {
  can_manage_team: boolean;
  can_invite_member: boolean;
  can_remove_member: boolean;
  can_manage_project: boolean;
  can_edit_document: boolean;
  can_view_document: boolean;
  can_delete_project: boolean;
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
