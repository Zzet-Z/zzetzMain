根据当前结构化摘要和本轮新增信息，输出更新后的 JSON 摘要。

要求：
1. 只能输出一个 JSON 对象，不要输出解释、标题或额外文本。
2. 只提取用户明确表达过的信息，不要臆测。
3. 保留已有字段；本轮没有新增的信息不要随意删除。
4. 如果当前阶段的信息已经足够支持进入下一阶段，就把对应的 ready 字段设为 `true`。
5. 如果信息还不够，就不要强行设为 `true`。

建议字段：
- `website_type`: 网站类型，例如“个人作品页”
- `visual_direction`: 视觉方向，例如“极简高级”
- `audience`: 目标受众
- `positioning`: 网站定位/主要目标
- `core_message`: 想传达的核心印象或主张
- `content_sections`: 主要内容模块数组
- `features`: 功能需求数组
- `positioning_ready`: 布尔值
- `content_ready`: 布尔值
- `features_ready`: 布尔值

阶段判断规则：
- 当前阶段是 `positioning` 时，如果用户已经说明了服务对象、目标受众、主要目标或核心传达方向中的关键信息，可设 `positioning_ready: true`
- 当前阶段是 `content` 时，如果用户已经说明想展示的主要内容、栏目或页面模块，可设 `content_ready: true`
- 当前阶段是 `features` 时，如果用户已经说明需要的交互、表单、预约、筛选、上传、联系方式等功能，可设 `features_ready: true`
