import { createRoot } from "react-dom/client";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import App from "./App";
import "./index.css";
createRoot(document.getElementById("root")!).render(
  <TooltipProvider>
    <App />
    <Toaster theme="light" richColors closeButton />
  </TooltipProvider>,
);
