from enum import Enum

class BugStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    REOPENED = 'reopened'

BUG_STATUS_DISPLAY = {
    BugStatus.PENDING.value: '待处理',
    BugStatus.IN_PROGRESS.value: '处理中',
    BugStatus.RESOLVED.value: '已解决',
    BugStatus.CLOSED.value: '已关闭',
    BugStatus.REOPENED.value: '重新打开'
}

#创建一个枚举类，用于BUG的分类，有 功能 界面 性能 兼容性 其他
class BugCategory(Enum):
    FUNCTIONAL = '功能'
    UI = '界面'
    PERFORMANCE = '性能'
    COMPATIBILITY = '兼容性'
    OTHER = '其他'

BUG_CATEGORY_DISPLAY = {
    BugCategory.FUNCTIONAL.value: '功能',
    BugCategory.UI.value: '界面',
    BugCategory.PERFORMANCE.value: '性能',
    BugCategory.COMPATIBILITY.value: '兼容性',
    BugCategory.OTHER.value: '其他'
}

#创建一个枚举类，用于BUG的类型，有 需求 缺陷 任务 建议 其他
class BugType(Enum):
    REQUIREMENT = '需求'
    BUG = '缺陷'
    TASK = '任务'   
    SUGGESTION = '建议'
    OTHER = '其他'

BUG_TYPE_DISPLAY = {
    BugType.REQUIREMENT.value: '需求',
    BugType.BUG.value: '缺陷',
    BugType.TASK.value: '任务',
    BugType.SUGGESTION.value: '建议',
    BugType.OTHER.value: '其他'
}