import React from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
} from "react-router-dom";
import Login from './pages/Login'
import Main from './pages/Main';
import {Provider} from 'react-redux'
import store from './store'

export default () => {
    const hello : string = "HELLO2";
    return <>
        <Provider store={store}>
            <Router>
                <Switch>
                <Route path="/" exact>
                    <Main />
                </Route>
                <Route path="/main">
                    <Login />
                </Route>
                </Switch>
            </Router>
        </Provider>
    </>
}