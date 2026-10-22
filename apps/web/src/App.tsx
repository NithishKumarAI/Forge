import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { CurriculumPage } from "./pages/CurriculumPage";
import { CurriculumBuilderPage } from "./pages/CurriculumBuilderPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LearnPage } from "./pages/LearnPage";
import { TutorPage } from "./pages/TutorPage";
import { SettingsPage } from "./pages/SettingsPage";
import { PracticePage } from "./pages/PracticePage";
import { TopicPage } from "./pages/TopicPage";
import { TransferPage } from "./pages/TransferPage";
import { ReviewPage } from "./pages/ReviewPage";

const TimedTestPage = lazy(() => import("./pages/TimedTestPage").then(module => ({default:module.TimedTestPage})));
const InterviewPage = lazy(() => import("./pages/InterviewPage").then((module) => ({ default: module.InterviewPage })));
const InterviewReportPage = lazy(() => import("./pages/InterviewPage").then((module) => ({ default: module.InterviewReportPage })));
const ArenaHome = lazy(() => import("./pages/ArenaPage").then((module) => ({ default: module.ArenaHome })));
const ArenaProblemPage = lazy(() => import("./pages/ArenaPage").then((module) => ({ default: module.ArenaProblemPage })));
const BeginnerExercisePage = lazy(() => import("./pages/BeginnerExercisePage").then((module) => ({ default: module.BeginnerExercisePage })));
const ConceptLearnPage = lazy(() => import("./pages/ConceptLearnPage").then((module) => ({ default: module.ConceptLearnPage })));

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="curriculum" element={<CurriculumPage />} />
        <Route path="curriculum/new" element={<CurriculumBuilderPage />} />
        <Route path="curriculum/drafts/:curriculumId" element={<CurriculumBuilderPage />} />
        <Route path="topics/:topicId" element={<TopicPage />} />
        <Route path="topics/:topicId/learn" element={<LearnPage />} />
        <Route path="topics/:topicId/tutor" element={<TutorPage />} />
        <Route path="topics/:topicId/practice" element={<PracticePage />} />
        <Route path="topics/:topicId/transfer" element={<TransferPage />} />
        <Route path="concepts/:stepKey" element={<Suspense fallback={<div>Loading concept…</div>}><ConceptLearnPage /></Suspense>} />
        <Route path="arena" element={<Suspense fallback={<div>Loading Arena…</div>}><ArenaHome /></Suspense>} />
        <Route path="arena/:track" element={<Suspense fallback={<div>Loading Arena…</div>}><ArenaHome /></Suspense>} />
        <Route path="arena/exercises/:key" element={<Suspense fallback={<div>Loading exercise…</div>}><BeginnerExercisePage /></Suspense>} />
        <Route path="arena/problems/:key" element={<Suspense fallback={<div>Loading problem…</div>}><ArenaProblemPage /></Suspense>} />
        <Route path="review" element={<ReviewPage />} />
        <Route path="tests" element={<Suspense fallback={<div>Loading tests…</div>}><TimedTestPage/></Suspense>} />
        <Route path="tests/:testId" element={<Suspense fallback={<div>Loading test…</div>}><TimedTestPage/></Suspense>} />
        <Route path="interview" element={<Suspense fallback={<div>Loading interviews…</div>}><InterviewPage /></Suspense>} />
        <Route path="interview/:sessionId" element={<Suspense fallback={<div>Loading interview…</div>}><InterviewPage /></Suspense>} />
        <Route path="interview/:sessionId/report" element={<Suspense fallback={<div>Loading report…</div>}><InterviewReportPage /></Suspense>} />
        <Route path="guidance" element={<TutorPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
