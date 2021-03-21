import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import Button from '../components/Button';
import DatePicker from '../components/DatePicker';
import OutLineTextField from '../components/OutLineTextField';
import { addTodo } from '../data/todos/todosSlice';
import { io } from 'socket.io-client';
const socket = io("http://localhost:5000")

socket.on("taskComplete", function(data){
    console.log(data)
})

socket.on("crawlingComplete", function(data){
    console.log(data)
})

export default (props) => {
    const dispatch = useDispatch()
    const handleButton = () => {
        dispatch(addTodo(Math.random()))
        socket.emit("runCrawling",{
            index:"kospi",
            startDate: "20210308",
            endDate: "20210310"
        })
    }
    return <>
        <style jsx>{`
            .container{
                @apply flex flex-col;
            }
        `}</style>
        <div className={"container"}>
            <h4>일자별 주식 및 시가총액</h4>
            <div className={"flex"}>
                <DatePicker/>
                <DatePicker/>
                <Button onClick={handleButton}>가져오기</Button>
            </div>
        </div>
    </>
}