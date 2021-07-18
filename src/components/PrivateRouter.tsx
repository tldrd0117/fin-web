import React from 'react'
import { useSelector } from 'react-redux';
import { Redirect, Route } from 'react-router';
import { RootState } from '../data/root/rootReducer';

export default function PrivateRoute({ children, ...rest }) {
    const { token } = useSelector((state:RootState) => state.user)
    return (
      <Route
        {...rest}
        render={({ location }) =>
            token ? (
            children
          ) : (
            <Redirect
              to={{
                pathname: "/login",
                state: { from: location }
              }}
            />
          )
        }
      />
    );
  }