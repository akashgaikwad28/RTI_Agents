// @ts-nocheck
import { default as __fd_glob_26 } from "../src/content/docs/agents/meta.json?collection=meta"
import * as __fd_glob_25 from "../src/content/docs/agents/tracker_agent.mdx?collection=docs"
import * as __fd_glob_24 from "../src/content/docs/agents/router_agent.mdx?collection=docs"
import * as __fd_glob_23 from "../src/content/docs/agents/reviewer_agent.mdx?collection=docs"
import * as __fd_glob_22 from "../src/content/docs/agents/retrieval_agent.mdx?collection=docs"
import * as __fd_glob_21 from "../src/content/docs/agents/reflection_agent.mdx?collection=docs"
import * as __fd_glob_20 from "../src/content/docs/agents/formatter_agent.mdx?collection=docs"
import * as __fd_glob_19 from "../src/content/docs/agents/classifier_agent.mdx?collection=docs"
import * as __fd_glob_18 from "../src/content/docs/agents/approval_agent.mdx?collection=docs"
import * as __fd_glob_17 from "../src/content/docs/agents/AGENT_SYSTEM_OVERVIEW.mdx?collection=docs"
import * as __fd_glob_16 from "../src/content/docs/skills.mdx?collection=docs"
import * as __fd_glob_15 from "../src/content/docs/security.mdx?collection=docs"
import * as __fd_glob_14 from "../src/content/docs/roadmap.mdx?collection=docs"
import * as __fd_glob_13 from "../src/content/docs/rag-pipeline.mdx?collection=docs"
import * as __fd_glob_12 from "../src/content/docs/observability.mdx?collection=docs"
import * as __fd_glob_11 from "../src/content/docs/multilingual-translation.mdx?collection=docs"
import * as __fd_glob_10 from "../src/content/docs/multi-agent.mdx?collection=docs"
import * as __fd_glob_9 from "../src/content/docs/legacy-migration-guide.mdx?collection=docs"
import * as __fd_glob_8 from "../src/content/docs/interview-questions.mdx?collection=docs"
import * as __fd_glob_7 from "../src/content/docs/index.mdx?collection=docs"
import * as __fd_glob_6 from "../src/content/docs/evaluation.mdx?collection=docs"
import * as __fd_glob_5 from "../src/content/docs/deployment.mdx?collection=docs"
import * as __fd_glob_4 from "../src/content/docs/database-architecture.mdx?collection=docs"
import * as __fd_glob_3 from "../src/content/docs/data-pipeline-architecture.mdx?collection=docs"
import * as __fd_glob_2 from "../src/content/docs/dashboard.mdx?collection=docs"
import * as __fd_glob_1 from "../src/content/docs/architecture.mdx?collection=docs"
import * as __fd_glob_0 from "../src/content/docs/api-reference.mdx?collection=docs"
import { server } from 'fumadocs-mdx/runtime/server';
import type * as Config from '../source.config';

const create = server<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>({"doc":{"passthroughs":["extractedReferences"]}});

export const docs = await create.doc("docs", "src/content/docs", {"api-reference.mdx": __fd_glob_0, "architecture.mdx": __fd_glob_1, "dashboard.mdx": __fd_glob_2, "data-pipeline-architecture.mdx": __fd_glob_3, "database-architecture.mdx": __fd_glob_4, "deployment.mdx": __fd_glob_5, "evaluation.mdx": __fd_glob_6, "index.mdx": __fd_glob_7, "interview-questions.mdx": __fd_glob_8, "legacy-migration-guide.mdx": __fd_glob_9, "multi-agent.mdx": __fd_glob_10, "multilingual-translation.mdx": __fd_glob_11, "observability.mdx": __fd_glob_12, "rag-pipeline.mdx": __fd_glob_13, "roadmap.mdx": __fd_glob_14, "security.mdx": __fd_glob_15, "skills.mdx": __fd_glob_16, "agents/AGENT_SYSTEM_OVERVIEW.mdx": __fd_glob_17, "agents/approval_agent.mdx": __fd_glob_18, "agents/classifier_agent.mdx": __fd_glob_19, "agents/formatter_agent.mdx": __fd_glob_20, "agents/reflection_agent.mdx": __fd_glob_21, "agents/retrieval_agent.mdx": __fd_glob_22, "agents/reviewer_agent.mdx": __fd_glob_23, "agents/router_agent.mdx": __fd_glob_24, "agents/tracker_agent.mdx": __fd_glob_25, });

export const meta = await create.meta("meta", "src/content/docs", {"agents/meta.json": __fd_glob_26, });