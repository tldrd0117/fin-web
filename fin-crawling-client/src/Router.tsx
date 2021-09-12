import React from 'react';
import {
    Router,
    Switch,
    Route,
    Link,
    Redirect
} from "react-router-dom";
import Login from './pages/Login'
import Main from './pages/Main';
import {useSelector} from 'react-redux'
import { ConnectedRouter } from 'connected-react-router';
import {history, RootState} from "./data/root/rootReducer"
import PrivateRouter from './components/PrivateRouter'
import CrawlingBoard from './containers/CrawlingBoard';

export default () => {
    return <>
        <ConnectedRouter history={history}>
            <Switch>
                <PrivateRouter path="/marcap" exect>
                    <Main SubComponent={CrawlingBoard}/>
                </PrivateRouter>
                <Route path="/login">
                    <Login />
                </Route>
                <Redirect path={"/"} to={"/marcap"}/>
            </Switch>
        </ConnectedRouter>
    </>
}