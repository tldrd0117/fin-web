import { combineReducers } from "redux";
import todosReducer from "../todos/todosSlice";
import crawlingReducer from "../crawling/crawlingSlice";
import crawlingHistoryReducer from "../crawling/crawlingHistorySlice";
import socketReducer from "../socket/socketSlice"
import userReducer from "../user/userSlice"
import taskCalendarReducer from "../task/taskCalendarSlice"
import taskScheduleReducer from '../task/taskScheduleSlice'
import taskProgressReducer from '../task/taskProgressSlice'
import taskPoolInfoReducer from '../task/taskPoolInfoSlice'
import taskHistoryReducer from '../task/taskHistorySlice'
import { connectRouter } from 'connected-react-router'
import { createBrowserHistory } from 'history'

export const history = createBrowserHistory()

const task = combineReducers({
    calendar: taskCalendarReducer,
    poolInfo: taskPoolInfoReducer,
    schedule: taskScheduleReducer,
    progress: taskProgressReducer,
    history: taskHistoryReducer
})

const rootReducer = combineReducers({
    todos: todosReducer,
    crawling: crawlingReducer,
    crawlingHistory: crawlingHistoryReducer,
    socket: socketReducer,
    user: userReducer,
    router: connectRouter(history),
    task
})


export default rootReducer
export type RootState = ReturnType<typeof rootReducer>

