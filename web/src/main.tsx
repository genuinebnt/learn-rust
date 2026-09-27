import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigate, Outlet, RouterProvider, createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import { SectionPage } from "./pages/SectionPage";
import { TrackPage } from "./pages/TrackPage";
import { Workspace } from "./workspace/Workspace";
import "./styles/design.css";
import "./styles/app.css";

const rootRoute = createRootRoute({ component: Outlet });

const routes = [
  // Today is designed but needs the review queue (a later phase); start on DSA until then.
  createRoute({ getParentRoute: () => rootRoute, path: "/", component: () => <Navigate to="/dsa" /> }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa", component: () => <SectionPage area="dsa" /> }),
  createRoute({ getParentRoute: () => rootRoute, path: "/rust", component: () => <SectionPage area="rust" /> }),
  createRoute({ getParentRoute: () => rootRoute, path: "/build", component: () => <SectionPage area="build" /> }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/t/$track",
    component: function Track() {
      const { track } = trackRoute.useParams();
      return <TrackPage slug={track} />;
    },
  }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/p/$id",
    component: function Problem() {
      const { id } = problemRoute.useParams();
      return <Workspace id={id} />;
    },
  }),
] as const;
const trackRoute = routes[4];
const problemRoute = routes[5];

const router = createRouter({ routeTree: rootRoute.addChildren([...routes]) });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 5_000, refetchOnWindowFocus: false } } });

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
