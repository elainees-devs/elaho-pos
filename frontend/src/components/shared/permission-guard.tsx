import { PermissionCode } from "@/types/enums/permission.enums"
import React from "react"

// Wraps children, only renders if user has required permission
// Used throughout the app to conditionally show UI elements
export interface PermissionGuardProps{
    permission: PermissionCode
    children: React.ReactNode
    fallback: React.ReactNode
}