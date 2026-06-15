import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export const formatDate = (date) => dayjs(date).format('MMM D, YYYY')
export const formatDateTime = (date) => dayjs(date).format('MMM D, YYYY h:mm A')
export const formatTime = (date) => dayjs(date).format('h:mm A')
export const timeAgo = (date) => dayjs(date).fromNow()
