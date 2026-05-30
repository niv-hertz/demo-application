import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { TodoPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteTodo from "./DeleteTodo"
import EditTodo from "./EditTodo"

interface TodoActionsMenuProps {
  todo: TodoPublic
}

export const TodoActionsMenu = ({ todo }: TodoActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditTodo todo={todo} onSuccess={() => setOpen(false)} />
        <DeleteTodo id={todo.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
