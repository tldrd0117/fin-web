import { createSlice } from "@reduxjs/toolkit";

const todosSlice = createSlice({
    name: "todos",
    initialState: [],
    reducers:{
        addTodo: (state, action) => {
            state.push(action.payload)
        },
        toggleTodo: (state, action) => {
            const todo = state[action.payload.index]
            todo.completed = !todo.completed
        },
        removeTodo: (state, action) => {
            return state.filter((todo, i) => i !== action.payload.index)
        }
    }
})

const { actions, reducer } = todosSlice
export const { addTodo, toggleTodo, removeTodo } = actions
export default reducer