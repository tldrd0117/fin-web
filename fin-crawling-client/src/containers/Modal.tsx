import React from 'react';
import ReactDOM from 'react-dom'

const modalRoot = document.getElementById('modal');
class Modal extends React.Component {
    el
    constructor(props) {
        super(props);
        this.el = document.createElement('div');
        this.el.className = "modal-container"
    }

    componentDidMount() {
        // Portal 엘리먼트는 Modal의 자식이 마운트된 후 DOM 트리에 삽입됩니다.
        // 요컨대, 자식은 어디에도 연결되지 않은 DOM 노드로 마운트됩니다.
        // 자식 컴포넌트가 마운트될 때 그것을 즉시 DOM 트리에 연결해야만 한다면,
        // 예를 들어, DOM 노드를 계산한다든지 자식 노드에서 'autoFocus'를 사용한다든지 하는 경우에,
        // Modal에 state를 추가하고 Modal이 DOM 트리에 삽입되어 있을 때만 자식을 렌더링해주세요.
        modalRoot.appendChild(this.el);
    }

    componentWillUnmount() {
        modalRoot.removeChild(this.el);
    }

    render() {
        return <>
            <style jsx global>{`
                .modal-container{
                    width: 100%;
                    height: 100%;
                    top: 0px;
                    left: 0px;
                    position: fixed;
                }
            `}</style>
            {
                ReactDOM.createPortal(
                    this.props.children,
                    this.el
                )
            }
        </>;
    }
}

export default Modal