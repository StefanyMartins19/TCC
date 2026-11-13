import { createBrowserRouter } from "react-router";
import { AppLayout } from "./components";
import {
  DashboardPage,
  HomePage,
  IndicatorsPage,
  MethodologyPage,
  SourcesPage,
  TerritorialPage,
} from "./pages";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AppLayout,
    children: [
      { index: true, Component: HomePage },
      { path: "dashboard", Component: DashboardPage },
      { path: "indicadores", Component: IndicatorsPage },
      { path: "indicadores/:id", Component: IndicatorsPage },
      { path: "territorial", Component: TerritorialPage },
      { path: "fontes", Component: SourcesPage },
      { path: "metodologia", Component: MethodologyPage },
      { path: "*", Component: HomePage },
    ],
  },
]);
