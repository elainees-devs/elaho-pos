import type { LucideIcon } from "lucide-react"
import type { PermissionCode } from "@/types/enums/permission.enums"

export interface SidebarMenuItem {
    id: string
    label: string
    icon: LucideIcon
    path: string
    requiredRoles?: string[]
    requiredPermissions?: PermissionCode[]
    children?: SidebarMenuItem[]
    group?: string
    order?: number
}
