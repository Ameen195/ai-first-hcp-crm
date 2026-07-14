import { configureStore } from '@reduxjs/toolkit';

const initialState = {
  interaction: null,
  loading: false,
  error: null,
};

function crmReducer(state = initialState, action) {
  switch (action.type) {
    case 'interaction/loading':
      return { ...state, loading: true, error: null };
    case 'interaction/success':
      return { ...state, loading: false, interaction: action.payload, error: null };
    case 'interaction/error':
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}

const store = configureStore({ reducer: crmReducer });
export default store;