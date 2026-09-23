import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { CurriculumPage } from "./pages/CurriculumPage";
import { CurriculumBuilderPage } from "./pages/CurriculumBuilderPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LearnPage } from "./pages/LearnPage";
import { SettingsPage } from "./pages/SettingsPage";
import { PracticePage } from "./pages/PracticePage";
import { TopicPage } from "./pages/TopicPage";
import { TransferPage } from "./pages/TransferPage";
import { ReviewPage } from "./pages/ReviewPage";

const InterviewPage = lazy(() => import("./pages/InterviewPage").then((module) => ({ default: module.InterviewPage })));
const InterviewReportPage = lazy(() => import("./pages/InterviewPage").then((module) => ({ default: module.InterviewReportPage })));

export default function App() {
  return <Routes><Route element={<Layout />}><Route index element={<DashboardPage />} /><Route path="curriculum" element={<CurriculumPage />} /><Route path="curriculum/new" element={<CurriculumBuilderPage />} /><Route path="curriculum/drafts/:curriculumId" element={<CurriculumBuilderPage />} /><Route path="topics/:topicId" element={<TopicPage />} /><Route path="topics/:topicId/learn" element={<LearnPage />} /><Route path="topics/:topicId/practice" element={<PracticePage />} /><Route path="topics/:topicId/transfer" element={<TransferPage />} /><Route path="review" element={<ReviewPage />} /><Route path="interview" element={<Suspense fallback={<div>Loading interviews…</div>}><InterviewPage /></Suspense>} /><Route path="interview/:sessionId" element={<Suspense fallback={<div>Loading interview…</div>}><InterviewPage /></Suspense>} /><Route path="interview/:sessionId/report" element={<Suspense fallback={<div>Loading report…</div>}><InterviewReportPage /></Suspense>} /><Route path="settings" element={<SettingsPage />} /><Route path="*" element={<Navigate to="/" replace />} /></Route></Routes>;
}
