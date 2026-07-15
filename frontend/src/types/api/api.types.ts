export interface APIResponse<T> {
  data: T
  message?: string
}
export interface ApiError {
    detail?: string;
    [field: string]: string|string[] | undefined
}
export interface PaginatedResponse<T>{
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
export interface LoginTokens{
  access: string;
  refresh: string;
}