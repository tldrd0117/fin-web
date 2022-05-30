import React, { useEffect } from 'react';
import {
    Router,
    Switch,
    Route,
    Link,
    Redirect
} from "react-router-dom";
import Login from './pages/Login'
import Main from './pages/Main';
import Join from './pages/Join'
import {useDispatch, useSelector} from 'react-redux'
import { ConnectedRouter } from 'connected-react-router';
import {history, RootState} from "./data/root/rootReducer"
import PrivateRouter from './components/PrivateRouter'
import CrawlingBoard from './containers/CrawlingBoard';
import FactorBoard from './containers/FactorBoard';
import SeibroBoard from './containers/SeibroBoard';
import { fetchPublicKey } from './data/user/userSlice';
import Modal from './containers/Modal'
import LoadingModal from './components/LoadingModal';

export default () => {
    const dispatch = useDispatch()
    const modal = useSelector((state: RootState) => state.modal)
    useEffect(()=>{
        dispatch(fetchPublicKey({}))
    },[])
    return <>
        <ConnectedRouter history={history}>
            <Switch>
                <PrivateRouter path="/marcap" exect>
                    <Main SubComponent={CrawlingBoard}/>
                </PrivateRouter>
                <PrivateRouter path="/factor" exect>
                    <Main SubComponent={FactorBoard}/>
                </PrivateRouter>
                <PrivateRouter path="/seibro" exect>
                    <Main SubComponent={SeibroBoard}/>
                </PrivateRouter>
                <Route path="/login">
                    <Login />
                </Route>
                <Route path="/join">
                    <Join />
                </Route>

                <Redirect path={"/"} to={"/marcap"}/>
            </Switch>
            {
                modal.LoadingModal?<LoadingModal/>:""
            }
            
        </ConnectedRouter>
    </>
}