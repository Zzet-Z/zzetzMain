# Personal Website Homepage And Intake Design

## 1. Overview

This document defines the MVP design for a product that helps non-technical users clarify and structure the requirements for a personal website. The MVP scope in this spec covers two user-facing surfaces:

- A marketing homepage that explains the product idea and attracts users through strong visual design
- A guided intake page that turns a user's vague ideas into a readable summary and a standard PRD

The downstream step of generating the actual website from the PRD is intentionally out of scope for this phase.

## 2. Product Positioning

The product is for ordinary users with no programming background who want their own website but do not know how to define it, describe it, or turn their ideas into something buildable.

The core promise is:

> You do not need to know how to code or write requirements. You only need to describe who you are, what you want to show, and what kind of impression you want to create. The system will guide you and produce a professional website brief and PRD.

This product is not positioned as "instant AI website generation" on the homepage. It is positioned as "structured guidance that turns vague intent into a professional website plan."

## 3. Target Users

The MVP should remain broad rather than narrow by profession. It should work for users such as:

- People who want a polished personal homepage
- People who want a portfolio site
- People who want a resume or profile site
- Freelancers or consultants who need a service presentation page
- Small teams or companies who need a simple company introduction page

The language should stay non-technical and avoid industry-heavy wording.

## 4. Goals And Non-Goals

### Goals

- Explain the product idea clearly through a high-design homepage
- Build trust that the product can help users create a beautiful and thoughtful website direction
- Guide users into a structured intake flow with minimal friction
- Let users choose a website business template and a visual style reference, with skip options
- Support image uploads during the conversation as reference materials
- Produce two outputs at the end of the conversation:
  - A short, readable summary for the user
  - A complete standard PRD in Markdown format
- Support revisiting the session later through a unique token without requiring login

### Non-Goals

- User accounts or authentication
- Payments or subscriptions
- Multi-user collaboration
- Full website generation
- Advanced image understanding pipelines
- Template marketplace or CMS

## 5. Visual Direction

The homepage should feel forward-looking, premium, and design-led. It should not look like a generic SaaS landing page.

The product should be designed mobile-first. Mobile compatibility is not a secondary polish item for this MVP. The homepage and intake flow should both assume that a large share of users will arrive and complete the process on phones.

The visual reference direction should borrow the following principles from the Apple design language described in the referenced Stitch design document:

- Strong rhythm created by alternating dark and light sections
- Very restrained use of accent color, reserved mainly for interactive elements
- Large-scale typography with significant whitespace
- Product outputs treated like display objects rather than dashboard widgets

The site should avoid excessive "AI glow" aesthetics, busy gradients, or a cluttered card-heavy layout. The design should communicate taste, calmness, and confidence.

Mobile-first visual constraints:

- Key value proposition and primary CTA must be visible quickly without excessive scrolling on phone screens
- Typography must remain premium-looking on mobile without collapsing into oversized headline blocks that crowd the viewport
- Visual showcase areas must remain legible and elegant in a single-column layout
- Touch targets must be sized for finger interaction rather than mouse precision

Reference:

- Apple design reference: https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/apple/DESIGN.md

## 6. Homepage Responsibilities

The homepage has two jobs:

1. Explain the product idea and reduce psychological friction
2. Push users toward starting the guided intake flow

The primary goal is understanding. The secondary goal is conversion into the intake page.

The homepage should make it obvious that:

- This product is for people who do not know how to code
- Users do not need to already know all their requirements
- The output is not just a chat transcript, but a structured deliverable

## 7. Homepage Information Architecture

The homepage should use a small number of sections with high visual quality. Five sections are sufficient for the MVP.

The homepage should be designed from the mobile layout upward, then expanded for tablet and desktop. The mobile version should preserve the premium feeling rather than becoming a stripped-down fallback.

### 7.1 Hero Section

The hero is the most important section and should combine visual impact with immediate clarity.

Recommended structure:

- Large headline
- Short subheadline
- Primary CTA to start the intake flow
- Secondary CTA to explain how it works
- A polished visual object representing either a future website preview or a refined requirements artifact

Mobile behavior:

- The CTA should remain above the fold on common phone viewport sizes
- The supporting visual should not push the headline and CTA too far downward
- The section should read as one clear story in a single column

Suggested message direction:

- Headline direction: "把你想要的网站，说出来。"
- Supporting direction: "不需要会编程，也不需要先写需求。通过一次引导式对话，整理出属于你的个人网站方案与标准 PRD。"

Primary CTA examples:

- "开始梳理我的网站"
- "开始定义我的个人网站"

### 7.2 Problem And Product Idea Section

This section explains why the product exists by focusing on real user pain:

- Users know they need a website but do not know what shape it should take
- Users can recognize websites they like but cannot express the design direction clearly
- Users do not know how to write a PRD or communicate requirements to a developer or AI

The response from the product should be framed as:

- First clarify who you are and what your site needs to do
- Then anchor the visual direction
- Then generate a professional output document

### 7.3 Three-Step Flow Section

This section should reduce anxiety and explain the process simply:

1. Choose a site type and optionally a style reference
2. Talk through your goals, content, and preferences
3. Receive a summary and a full PRD

The copy should explicitly signal that this is guided conversation, not a form the user must write alone.

### 7.4 Output Showcase Section

This section should show the outcome rather than the chat itself. Present two side-by-side deliverables:

- Website brief summary
- Standard PRD document

This helps users understand the value difference between this product and a generic chat assistant.

On mobile, these outputs should stack vertically and remain readable as strong content previews rather than tiny desktop cards shrunk to fit.

### 7.5 Closing CTA Section

The page should end with a simple restatement:

- No coding required
- Professional output
- One clear next step

The closing CTA should remain consistent with the hero CTA.

## 8. Intake Page Responsibilities

The intake page has one job:

> Guide a non-technical user from vague intent to a structured website summary and PRD.

It should feel guided rather than technical. The user should feel that the system is organizing their thoughts, not interrogating them.

## 9. Intake Page Flow

The intake page should use a staged flow with a top progress indicator and a chat-led primary interaction model.

The intake flow must be fully usable on mobile. A phone user should be able to select templates, review style references, upload images, answer prompts, and read the final summary and PRD access state without needing a desktop browser.

Recommended steps:

1. Template
2. Style
3. Positioning
4. Content
5. Features
6. Generate

### 9.1 Step 1: Business Template Selection

This step helps users choose the general shape of the site before they need to explain details.

Initial template options:

- Personal portfolio
- Personal resume
- Personal brand
- Service introduction
- Company introduction
- Booking or consulting page
- Other
- Skip

The template acts as an anchor for later questions and default content structure. It should not rigidly constrain the final PRD.

### 9.2 Step 2: Style Reference Selection

This step presents a set of homepage-style previews and allows the user to choose one or skip.

Initial style directions:

- Minimal premium
- Modern professional
- Visual portfolio
- Warm and trustworthy
- Futuristic
- Skip

The chosen style should influence the visual direction recorded in the PRD. It should not automatically force a layout or content model.

### 9.3 Step 3: Positioning

The system should guide the user to express:

- Who they are
- Who the site is for
- What visitors should do after seeing the site
- What kind of feeling the site should create

This step should establish the website's purpose before discussing detailed features.

### 9.4 Step 4: Content

The system should gather content modules dynamically based on the selected template and the user's answers.

Examples:

- Portfolio-oriented flows should ask about projects, case studies, media, and presentation style
- Resume-oriented flows should ask about experience, skills, projects, education, and contact channels
- Company-oriented flows should ask about business overview, services, team, cases, and contact methods

The system should turn freeform input into structured content modules.

### 9.5 Step 5: Features And Boundaries

The system should confirm practical needs in user-friendly language, such as:

- Contact form
- Booking link
- Blog or articles
- Case filters
- FAQ
- Single-page or multi-page structure
- Things the user definitely does not want

This should never feel like a technical requirements interview.

### 9.6 Step 6: Generate

Once enough information is available, the user should not need to continue participating. The system should move into finalization and produce:

- A user-friendly summary
- A standard PRD document in Markdown
- A session token or revisit link for future edits

## 10. Intake Page Layout

Desktop layout should behave like a three-part experience:

- Top progress bar
- Main conversation area
- Real-time summary and attachments area

Mobile should collapse into a single-column flow while preserving the step model. The mobile version should be treated as a first-class experience, not a simplified fallback.

### 10.1 Top Area

- Step indicator
- Session status message such as "正在梳理定位" or "正在生成需求文档"

Mobile requirements:

- Step progress should remain visible without taking too much vertical space
- Status information should stay compact and readable
- Sticky behavior is acceptable if it improves orientation without blocking content

### 10.2 Main Conversation Area

- Chat-like interaction
- Short assistant prompts
- Freeform user input
- Optional quick-select responses when users need help expressing themselves

Mobile requirements:

- The input area should remain usable above the software keyboard
- Quick-select options should be tappable and not densely packed
- Message width and spacing should prioritize readability on narrow screens

### 10.3 Summary Sidebar

The summary should update during the conversation and include:

- Site type
- Audience
- Positioning
- Visual direction
- Page structure
- Content modules
- Functional requirements

This sidebar helps users trust that the system is interpreting them correctly.

On mobile, this should convert into a collapsible summary panel or step-linked summary section rather than a persistent side column.

### 10.4 Attachment Area

The page should support image uploads during the conversation. Users may upload:

- Personal photos
- Work samples
- Brand assets
- Screenshots of websites they like
- Reference layouts or visual inspiration

Attachments should be previewed in the session and recorded in the final PRD as supporting materials.

Mobile requirements:

- Image upload should support direct photo selection from the phone
- Previews should remain lightweight and vertically scannable
- Upload and removal actions should be easy to perform with touch

## 11. Output Requirements

Each completed session should produce two outputs.

### 11.1 User Summary

This is a concise, readable summary meant for users to quickly confirm the result of the conversation. It should be simple and human-readable.

### 11.2 PRD Document

The PRD should be a standard Markdown document suitable for downstream use by developers or another AI system.

The PRD depth should match a standard product-level document, including at minimum:

- Project objective
- Target audience
- Website type
- Visual direction
- Visitor goals
- Information architecture or page structure
- Module-level content summary
- Feature requirements
- Constraints and exclusions
- Attachment list and descriptions

This PRD should be sufficiently structured to serve as the input for a later AI website generation step.

## 12. Session Model

The MVP should not require login. Instead, every intake session should be identified by a unique token.

This token must support:

- Returning to the session later
- Reviewing the current summary
- Editing or continuing the requirement clarification later
- Accessing the final PRD document

The token should represent a single isolated session. All messages, summaries, attachments, and output documents must remain bound to that token.

## 13. Concurrency Design

The MVP is designed for internal testing rather than public-scale launch.

Concurrency rule:

- At most 5 active sessions may occupy LLM processing capacity at the same time
- The 6th session and beyond enter a queue
- Queued sessions start only when one of the currently active sessions reaches the completed document state and frees a slot

Important clarification:

- Opening the page does not consume a concurrency slot
- A slot is consumed only when a session enters the active LLM-guided processing phase

### 13.1 Session States

Recommended session states:

- `draft`
- `queued`
- `active`
- `generating_document`
- `completed`
- `failed`

The expected meaning:

- `draft`: Session exists but has not entered active LLM processing
- `queued`: Waiting for one of the 5 active slots
- `active`: Ongoing guided interaction with LLM support
- `generating_document`: Final summary and PRD are being produced
- `completed`: Outputs are ready and the slot is released
- `failed`: Processing failed and can be retried

### 13.2 Queue Behavior

- Different sessions may proceed in parallel up to the 5-session limit
- A single session must remain serial internally
- A session cannot run multiple LLM turns or multiple document generations at the same time
- New queued users should see a clear waiting state and queue feedback

Users in the queue should still be allowed to:

- Choose a template
- Choose a style reference
- Upload images
- Prepare an initial message

They should not feel blocked from all interaction while waiting.

## 14. Technical Architecture

The recommended MVP stack is:

- Frontend: React + Tailwind CSS
- Backend: Python Flask
- Database: SQLite for the first internal test
- File storage: local filesystem
- Final document format: Markdown

This should be implemented as a monolithic application with clear module boundaries.

The frontend should follow a mobile-first responsive strategy:

- Default layout and spacing rules should target phone screens first
- Tablet and desktop layouts should progressively enhance the structure
- Component APIs should avoid assuming hover, wide horizontal space, or mouse-first interactions

### 14.1 Frontend Routes

Minimum routes:

- `/`
- `/session/:token`

The React frontend should treat these routes as responsive surfaces rather than separate desktop and mobile variants. A single component system with mobile-first Tailwind breakpoints is preferred for the MVP.

### 14.2 Backend Responsibilities

Recommended backend modules:

- `sessions`
- `chat`
- `uploads`
- `summaries`
- `documents`
- `templates`

### 14.3 Data Persistence

Recommended tables:

- `sessions`
- `messages`
- `attachments`
- `summary_snapshots`
- `documents`

Suggested session fields:

- `token`
- `status`
- `selected_template`
- `selected_style`
- `queue_position`
- `started_at`
- `completed_at`
- `last_activity_at`
- `created_at`
- `updated_at`

Recommended attachment fields:

- `session_token`
- `file_path`
- `file_name`
- `mime_type`
- `caption`
- `message_id`
- `created_at`

Recommended document fields:

- `session_token`
- `summary_text`
- `prd_markdown`
- `status`
- `version`
- `created_at`
- `updated_at`

The real-time summary should be stored in structured JSON form rather than only prose so that it can later support AI website generation more reliably.

### 14.4 LLM Processing Model

The backend should not rely on long synchronous request handling for the full chat lifecycle.

Preferred model:

- Frontend sends a user message
- Backend stores the message
- Backend schedules an assistant turn job
- A worker processes the LLM request
- Frontend receives progress and output through polling or SSE

This keeps the web layer from being blocked and makes queue management practical even in the MVP.

## 15. Error Handling

Errors must be expressed in human language because the target users are non-technical.

Homepage:

- If the service is unavailable, show a short retry message without technical details

Intake page:

- Invalid or expired token: explain that the session link may no longer be valid and offer restart
- Upload failure: allow retry without blocking the rest of the flow
- PRD generation failure: preserve the summary if possible and offer document regeneration
- Weak or vague user input: do not error; instead provide examples and guided options

## 16. MVP Success Criteria

The MVP is successful if it can do the following reliably:

- Present the product clearly through the homepage
- Lead users into the intake page through a strong CTA
- Support template selection, style selection, guided conversation, and image upload
- Continuously build a structured summary during the session
- Produce a readable user summary
- Produce a standard Markdown PRD
- Preserve the session through a unique token for later return and modification
- Work well on mobile browsers, including the full intake flow and final output access

## 17. Recommended Implementation Order

The implementation should proceed in this order:

1. Define the structured summary schema and PRD schema
2. Build backend session, storage, and document-generation foundations
3. Design and implement the intake page flow mobile-first
4. Build the homepage visual experience mobile-first, then expand it for larger screens once product messaging is fully grounded

This order reduces rework because the homepage should accurately reflect the real product flow, and the intake page should be built around the final output model.

## 18. Final Product Logic

The system has three layers of value that must stay distinct:

- The homepage sells taste and clarity
- The intake page sells guided expression
- The backend output sells professional deliverables

If those three layers stay cleanly separated, the product will feel more intentional and credible than a generic "AI website chat" experience.
