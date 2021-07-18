import { Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import Card from '../components/Card';
import {fetchToken} from '../data/user/userSlice'
import * as Yup from 'yup'
import OutLineFormTextField from '../components/OutLineFormTextField';
import { RootState } from '../data/root/rootReducer';

export default () => {
    const dispatch = useDispatch()
    const {errorMsg} = useSelector((state:RootState)=>state.user)
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
            .errMsg{
                width: 80%;
            }
        `}</style>
        <Card className={"flex flex-col items-center card"}>
            <Formik
                initialValues={{
                    username: '',
                    password: ''
                }}
                validationSchema={Yup.object({
                    username: Yup.string()
                        .max(20, "아이디가 너무 깁니다")
                        .required("아이디를 입력하세요")
                        ,
                    password: Yup.string()
                        .required("비밀번호를 입력하세요")

                })}
                onSubmit={(values, { setSubmitting })=>{
                    setSubmitting(true);
                    setTimeout(() => {
                        dispatch(fetchToken(values))
                        setSubmitting(false);
                    }, 400);
                }}
                >
                    {
                        formik => (
                        <Form className={"flex flex-col items-center w-full"}>
                            <OutLineFormTextField 
                                name={"username"}
                                wrapperClassName={"textfield"}
                                type={"text"} 
                                formik={formik}
                                label={"아이디"}  />
                            <OutLineFormTextField
                                name={"password"}
                                wrapperClassName={"textfield"}
                                type={"password"}
                                formik={formik}  
                                label={"비밀번호"} />
                            {errorMsg?<div className={"text-sm text-red-500 mt-2 errMsg"}>{errorMsg}</div>:null}
                            <Button type={"submit"}
                                disabled={formik.isSubmitting}
                                className={"button"} >로그인</Button>
                        </Form>
                        )
                    }
                
            </Formik>
        </Card>
        
    </>
}