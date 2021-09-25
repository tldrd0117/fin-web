import React, { useState } from 'react';

export default (props) => {
    return <>
        <style jsx>{`
        `}</style>
        {props.isShow? props.show : props.hide}
    </>
}
