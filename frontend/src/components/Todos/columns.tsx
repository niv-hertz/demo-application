import { useMutation, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"

import type { TodoPublic } from "@/client"
import { TodosService } from "@/client"
import { Checkbox } from "@/components/ui/checkbox"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { TodoActionsMenu } from "./TodoActionsMenu"

function ToggleComplete({ todo }: { todo: TodoPublic }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => TodosService.toggleComplete({ id: todo.id }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["todos"] })
    },
  })

  return (
    <Checkbox
      checked={todo.is_completed}
      onCheckedChange={() => mutation.mutate()}
      disabled={mutation.isPending}
      aria-label="Mark complete"
    />
  )
}

export const columns: ColumnDef<TodoPublic>[] = [
  {
    accessorKey: "is_completed",
    header: "Done",
    cell: ({ row }) => <ToggleComplete todo={row.original} />,
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => (
      <Tooltip>
        <TooltipTrigger asChild>
          <span
            className={cn(
              "font-medium whitespace-nowrap",
              row.original.is_completed && "line-through text-muted-foreground",
            )}
          >
            {row.original.title}
          </span>
        </TooltipTrigger>
        <TooltipContent>{row.original.title}</TooltipContent>
      </Tooltip>
    ),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => {
      const description = row.original.description
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !description && "italic",
          )}
        >
          {description || "No description"}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <TodoActionsMenu todo={row.original} />
      </div>
    ),
  },
]
