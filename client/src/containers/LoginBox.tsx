import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import Card from '../components/Card';
import OutLineTextField from '../components/OutLineTextField';

export default () => {
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
                width: 100%;
                height: 60px;
            }
        `}</style>
        <Card className={"flex flex-col items-center card"}>
            <OutLineTextField className={"textfield"} label={"아이디"} />
            <OutLineTextField className={"textfield"} label={"비밀번호"} />
            <Link to="/main" className={"link"}>
                <Button className={"button"} variant="outlined" color="primary">로그인</Button>
            </Link>
        </Card>
    </>
}