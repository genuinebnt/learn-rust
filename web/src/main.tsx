import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigate, Outlet, RouterProvider, createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import { DsaPage } from "./pages/DsaPage";
import { PatternProblems } from "./pages/PatternProblems";
import { CalendarPage } from "./pages/CalendarPage";
import { DsaPlanPage } from "./pages/DsaPlanPage";
import { MockPage } from "./pages/MockPage";
import { DsaProblemPage } from "./pages/DsaProblemPage";
import { PatternPage } from "./pages/PatternPage";
import { ReviewPage } from "./pages/ReviewPage";
import { PracticePage } from "./pages/PracticePage";
import { LoginPage } from "./pages/LoginPage";
import { ProgressPage } from "./pages/ProgressPage";
import { SectionPage } from "./pages/SectionPage";
import { TrackPage } from "./pages/TrackPage";
import { Workspace } from "./workspace/Workspace";
import "./styles/design.css";
import "./styles/app.css";
import "./styles/catalog.css";
import "./styles/progress.css";
import "./styles/dsa.css";
import "./styles/mock.css";
import "./styles/lessons.css";
import "./styles/review.css";
import "./styles/problem.css";
import "./styles/calendar.css";

const rootRoute = createRootRoute({ component: Outlet });

const routes = [
  // Today is designed but needs the review queue (a later phase); start on DSA until then.
  createRoute({ getParentRoute: () => rootRoute, path: "/", component: () => <Navigate to="/dsa" /> }),
  createRoute({ getParentRoute: () => rootRoute, path: "/login", component: LoginPage }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa", component: DsaPage }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa/plan", component: DsaPlanPage }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa/calendar", component: CalendarPage }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa/mock", component: MockPage }),
  createRoute({ getParentRoute: () => rootRoute, path: "/dsa/review", component: ReviewPage }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/dsa/patterns/$code",
    component: function Patterns() {
      const { code } = patternsRoute.useParams();
      return <PatternPage code={code} />;
    },
  }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/dsa/practice/$code",
    component: function Practice() {
      const { code } = practiceRoute.useParams();
      return <PracticePage code={code} />;
    },
  }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/d/$slug",
    component: function DsaProblem() {
      const { slug } = dsaProblemRoute.useParams();
      return <DsaProblemPage key={slug} slug={slug} />;
    },
  }),
  createRoute({ getParentRoute: () => rootRoute, path: "/rust", component: () => <SectionPage area="rust" /> }),
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
  createRoute({ getParentRoute: () => rootRoute, path: "/progress", component: ProgressPage }),
  createRoute({
    getParentRoute: () => rootRoute,
    path: "/dsa/patterns/$code/problems",
    component: function PatternProblemsRoute() {
      const { code } = patternProblemsRoute.useParams();
      return <PatternProblems code={code} />;
    },
  }),
] as const;
const patternsRoute = routes[7];
const practiceRoute = routes[8];
const dsaProblemRoute = routes[9];
const trackRoute = routes[11];
const problemRoute = routes[12];
const patternProblemsRoute = routes[14];

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
