import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import Card from '../components/Card';
import OutLineTextField from '../components/OutLineTextField';
import {fetchToken} from '../data/user/userSlice'

export default () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const dispatch = useDispatch()
    const handleLogin = () => {
        dispatch(fetchToken({
            username,
            password
        }))
    }
    return <>
        <style jsx global>{`
            .card{
                width: 375px;
            }
            .textfield{
                width: 80%;
                margin-top: 30px;
            }
            .link{
                width: 80%;
                margin: 30px 0px ;
                text-decoration: none;
                height: 60px;
            }
            .button{
                width: 80%;
                margin: 30px 0px ;
                height: 60px;
            }
        `}</style>
        <Card className={"flex flex-col items-center card"}>
            <OutLineTextField value={username} onChange={(e)=>setUsername(e.target.value)} className={"textfield"} label={"아이디"}  />
            <OutLineTextField value={password} onChange={(e)=>setPassword(e.target.value)} className={"textfield"} label={"비밀번호"} />
            <Button onClick={handleLogin} className={"button"} >로그인</Button>
        </Card>
    </>
}