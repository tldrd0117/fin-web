import React from 'react'
import ReactDOM from 'react-dom';
import App from './App'
import './App.css';
import Modal from 'react-modal';

//bug fix
import _JSXStyle from 'styled-jsx/style';
 
if (typeof global !== 'undefined') {
  Object.assign(global, { _JSXStyle })
}

const appElement = document.getElementById('app');
Modal.setAppElement(appElement);
ReactDOM.render(<App/>, appElement);