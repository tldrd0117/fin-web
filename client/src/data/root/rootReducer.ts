import { combineReducers } from "redux";
import todosReducer from "../todos/todosSlice";
import crawlingReducer from "../crawling/crawlingSlice";
import socketReducer from "../socket/socketSlice"
const rootReducer = combineReducers({
    todos: todosReducer,
    crawling: crawlingReducer,
    socket: socketReducer
})

export default rootReducer
export type RootState = ReturnType<typeof rootReducer>
