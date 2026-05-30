import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useState } from "react"

import { TodosService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddTodo from "@/components/Todos/AddTodo"
import { columns } from "@/components/Todos/columns"
import PendingTodos from "@/components/Pending/PendingTodos"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

type FilterTab = "all" | "active" | "completed"

function getTodosQueryOptions() {
  return {
    queryFn: () => TodosService.readTodos({ skip: 0, limit: 100 }),
    queryKey: ["todos"],
  }
}

export const Route = createFileRoute("/_layout/todos")({
  component: Todos,
  head: () => ({
    meta: [
      {
        title: "Todos - FastAPI Template",
      },
    ],
  }),
})

function TodosTableContent() {
  const { data: todos } = useSuspenseQuery(getTodosQueryOptions())
  const [filter, setFilter] = useState<FilterTab>("all")

  const filtered = todos.data.filter((todo) => {
    if (filter === "active") return !todo.is_completed
    if (filter === "completed") return todo.is_completed
    return true
  })

  if (todos.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any todos yet</h3>
        <p className="text-muted-foreground">Add a new todo to get started</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <Tabs value={filter} onValueChange={(v) => setFilter(v as FilterTab)}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>
      </Tabs>
      <DataTable columns={columns} data={filtered} />
    </div>
  )
}

function TodosTable() {
  return (
    <Suspense fallback={<PendingTodos />}>
      <TodosTableContent />
    </Suspense>
  )
}

function Todos() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Todos</h1>
          <p className="text-muted-foreground">Create and manage your todos</p>
        </div>
        <AddTodo />
      </div>
      <TodosTable />
    </div>
  )
}
