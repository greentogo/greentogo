import { saveAuthToken } from './actions';

import { handleActions } from 'redux-actions';
import update from 'immutability-helper';

const reducer = handleActions({
    [saveAuthToken]: (state, action) => {
        if (action.payload.token) {
            return update(state, {
              authToken: {$set: action.payload.token}
            })
        } else {
            return state;
        }
    }
}, {
    authToken: null
});

export default reducer;
