import React from 'react'
import Modal from '../containers/Modal'
import ReactLoading from 'react-loading';

export default () => {
    return <>
        <style jsx>{`
            .bg{
                background-color: white;
                opacity: 0.8;
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0px;
                left: 0px;
            }
            .loading-back{
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0px;
                left: 0px;
            }
        `}</style>
        <Modal>
            <div className='bg' />
            <div className='loading-back flex justify-center items-center'>
                <ReactLoading type={"cubes"} color={"rgb(6, 182, 212)"} height={50} width={75} />
            </div>
        </Modal>
    </>
}