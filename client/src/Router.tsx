import React from 'react';
import {
    Router,
    Switch,
    Route,
    Link
} from "react-router-dom";
import Login from './pages/Login'
import Main from './pages/Main';
import {useSelector} from 'react-redux'
import { ConnectedRouter } from 'connected-react-router';
import {history, RootState} from "./data/root/rootReducer"
import PrivateRouter from './components/PrivateRouter'

export default () => {
    return <>
        <ConnectedRouter history={history}>
            <Switch>
                <PrivateRouter path="/" exact>
                    <Main/>
                </PrivateRouter>
                <Route path="/login">
                    <Login />
                </Route>
            </Switch>
        </ConnectedRouter>
    </>
}