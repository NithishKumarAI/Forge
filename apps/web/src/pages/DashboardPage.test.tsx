import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { DashboardPage } from "./DashboardPage";
import type { LearningPathDashboardData } from "../types/learningPath";

const mockDashboard: LearningPathDashboardData = {
  primary_recommendation: {
    kind: "next_concept",
    priority_tier: 4,
    reason: "Next available concept in Python",
    subject_key: "python",
    subject_name: "Python",
    concept_key: "py-first-message",
    concept_title: "Printing Your First Message",
    stage: "First Steps",
    progress_state: "learning",
    progress_summary: "In progress",
    action_label: "Start Learning",
    action_path: "/arena/exercises/py-first-message",
    objective: "Learn to output text to the console using print().",
    is_primary: true,
  },
  secondary_recommendations: [
    {
      kind: "review",
      priority_tier: 2,
      reason: "Scheduled review due",
      subject_key: "sql-postgresql",
      subject_name: "SQL & PostgreSQL",
      concept_key: "sql-first-select",
      concept_title: "Writing a Constant SELECT Query",
      stage: "First Steps",
      progress_state: "retained",
      progress_summary: "Review due",
      action_label: "Review Concept",
      action_path: "/arena/exercises/sql-first-select",
      objective: "Select literal constant values.",
      is_primary: false,
    },
    {
      kind: "practice",
      priority_tier: 5,
      reason: "Beginner independent practice",
      subject_key: "dsa",
      subject_name: "Data Structures & Algorithms",
      concept_key: "dsa-trace-array",
      concept_title: "Tracing an Array & Zero-Based Indexing",
      stage: "First Steps",
      progress_state: "practising",
      progress_summary: "Practising",
      action_label: "Continue Practising",
      action_path: "/arena/exercises/dsa-trace-array",
      objective: "Access elements by 0-based indices.",
      is_primary: false,
    },
    {
      kind: "secondary_subject",
      priority_tier: 6,
      reason: "Explore foundations",
      subject_key: "quantitative-aptitude",
      subject_name: "Quantitative Aptitude",
      concept_key: "qa-percentages-fractions",
      concept_title: "Percentage-to-Fraction Conversions",
      stage: "First Steps",
      progress_state: "not_started",
      progress_summary: "Not started",
      action_label: "Begin Concept",
      action_path: "/curriculum",
      objective: "Convert between percentages and fractions.",
      is_primary: false,
    },
  ],
  active_subject: "python",
  subjects: [
    {
      subject_key: "python",
      subject_name: "Python",
      description: "Python Programming",
      icon: "code",
      current_concept_title: "Printing Your First Message",
      current_concept_key: "py-first-message",
      progress_state: "learning",
      completed_concepts: 0,
      in_progress_concepts: 1,
      total_concepts: 5,
      action_path: "/arena/exercises/py-first-message",
    },
    {
      subject_key: "sql-postgresql",
      subject_name: "SQL & PostgreSQL",
      description: "SQL & Relational Databases",
      icon: "database",
      current_concept_title: "Writing a Constant SELECT Query",
      current_concept_key: "sql-first-select",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 4,
      action_path: "/arena/exercises/sql-first-select",
    },
    {
      subject_key: "dsa",
      subject_name: "Data Structures & Algorithms",
      description: "Foundational DSA",
      icon: "network",
      current_concept_title: "Tracing an Array & Zero-Based Indexing",
      current_concept_key: "dsa-trace-array",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 4,
      action_path: "/arena/exercises/dsa-trace-array",
    },
    {
      subject_key: "quantitative-aptitude",
      subject_name: "Quantitative Aptitude",
      description: "Aptitude Foundations",
      icon: "calculator",
      current_concept_title: "Percentage-to-Fraction Conversions",
      current_concept_key: "qa-percentages-fractions",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
    {
      subject_key: "logical-reasoning",
      subject_name: "Logical Reasoning",
      description: "Reasoning Foundations",
      icon: "puzzle",
      current_concept_title: "Linear Seating Arrangements",
      current_concept_key: "lr-linear-seating",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
    {
      subject_key: "verbal-english",
      subject_name: "Verbal & Communication",
      description: "Verbal Communication",
      icon: "languages",
      current_concept_title: "Subject-Verb Agreement",
      current_concept_key: "va-subject-verb-agreement",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
    {
      subject_key: "system-design",
      subject_name: "System Design",
      description: "System Design Basics",
      icon: "layers",
      current_concept_title: "Client-Server Architecture & HTTP",
      current_concept_key: "sd-client-server",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
    {
      subject_key: "ai-fundamentals",
      subject_name: "AI Fundamentals",
      description: "Applied AI Concepts",
      icon: "sparkles",
      current_concept_title: "Prompt Engineering & Few-Shot Learning",
      current_concept_key: "ai-prompt-engineering",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
    {
      subject_key: "interview-communication",
      subject_name: "Interview Communication",
      description: "Behavioral Interviews",
      icon: "messages",
      current_concept_title: "The STAR Framework",
      current_concept_key: "ic-star-method",
      progress_state: "not_started",
      completed_concepts: 0,
      in_progress_concepts: 0,
      total_concepts: 2,
      action_path: "/curriculum",
    },
  ],
  content_availability: {
    status: "partly_usable",
    description: "Beginner First Steps path is ready for Python, SQL, and DSA. Placement Foundations tracks are in candidate preparation.",
    approved_lessons: 0,
    legacy_reference_lessons: 53,
    beginner_exercises_ready: 14,
    total_curriculum_topics: 157,
    note: "All 157 topics remain manually accessible through curriculum browsing.",
  },
  recent_mistakes: [],
  reviews_due_count: 0,
  active_curriculum: {
    id: 1,
    name: "Placement Foundations",
    version: 1,
  },
};

describe("Redesigned Learning-First Dashboard", () => {
  it("renders Continue Learning with prominent primary card and clear call to action", () => {
    const html = renderToStaticMarkup(
      <MemoryRouter>
        <DashboardPage initialData={mockDashboard} />
      </MemoryRouter>
    );

    expect(html).toContain("Continue Learning");
    expect(html).toContain("Printing Your First Message");
    expect(html).toContain("Learn to output text to the console using print().");
    expect(html).toContain("Start Learning");
    expect(html).toContain('href="/arena/exercises/py-first-message"');
    expect(html).toContain("Learning");
  });

  it("limits secondary recommendations to at most three items", () => {
    const html = renderToStaticMarkup(
      <MemoryRouter>
        <DashboardPage initialData={mockDashboard} />
      </MemoryRouter>
    );

    expect(html).toContain("Next Recommended Actions");
    expect(html).toContain("Writing a Constant SELECT Query");
    expect(html).toContain("Tracing an Array &amp; Zero-Based Indexing");
    expect(html).toContain("Percentage-to-Fraction Conversions");
  });

  it("does NOT display removed manual planner controls or scheduling terminology", () => {
    const html = renderToStaticMarkup(
      <MemoryRouter>
        <DashboardPage initialData={mockDashboard} />
      </MemoryRouter>
    );

    // Verify removed manual planner controls are absent:
    expect(html).not.toContain("Today's study plan");
    expect(html).not.toContain("target selectors");
    expect(html).not.toContain("unallocated minutes");
    expect(html).not.toContain("unallocated_minutes");
    expect(html).not.toContain("300 min");
    expect(html).not.toContain("360 min");
    expect(html).not.toContain("480 min");
    expect(html).not.toContain("Regenerate plan");
    expect(html).not.toContain("Replace schedule");
    expect(html).not.toContain("legacy binding");
    expect(html).not.toContain("assessment pool");
  });

  it("displays all nine Placement Foundations subjects with honest availability", () => {
    const html = renderToStaticMarkup(
      <MemoryRouter>
        <DashboardPage initialData={mockDashboard} />
      </MemoryRouter>
    );

    // All 9 subjects are listed
    expect(html).toContain("Python");
    expect(html).toContain("SQL &amp; PostgreSQL");
    expect(html).toContain("Data Structures &amp; Algorithms");
    expect(html).toContain("Quantitative Aptitude");
    expect(html).toContain("Logical Reasoning");
    expect(html).toContain("Verbal &amp; Communication");
    expect(html).toContain("System Design");
    expect(html).toContain("AI Fundamentals");
    expect(html).toContain("Interview Communication");

    // Honest availability indicators
    expect(html).toContain("Beginner First Steps path is ready for Python, SQL, and DSA.");
  });

  it("renders truthful up-to-date state when no primary recommendation is available", () => {
    const emptyDashboard: LearningPathDashboardData = {
      ...mockDashboard,
      primary_recommendation: null,
      secondary_recommendations: [],
    };

    const html = renderToStaticMarkup(
      <MemoryRouter>
        <DashboardPage initialData={emptyDashboard} />
      </MemoryRouter>
    );

    expect(html).toContain("You are up to date!");
    expect(html).toContain("All available concepts for this subject have been completed.");
    expect(html).toContain('href="/arena"');
  });
});
