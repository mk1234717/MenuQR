import React, { createContext, useContext, useReducer } from 'react';

const CartContext = createContext();

const initialState = {
    items: [],
    total: 0,
};

const cartReducer = (state, action) => {
    switch (action.type) {
        case 'ADD_ITEM': {
            const existingItem = state.items.find(item => item.id === action.payload.id);
            
            if (existingItem) {
                return {
                    ...state,
                    items: state.items.map(item =>
                        item.id === action.payload.id
                            ? { ...item, quantity: item.quantity + (action.payload.quantity || 1) }
                            : item
                    ),
                    total: state.total + action.payload.price * (action.payload.quantity || 1),
                };
            }
            
            return {
                ...state,
                items: [...state.items, { ...action.payload, quantity: action.payload.quantity || 1 }],
                total: state.total + action.payload.price * (action.payload.quantity || 1),
            };
        }
        
        case 'REMOVE_ITEM':
            return {
                ...state,
                items: state.items.filter(item => item.id !== action.payload),
                total: state.total - (state.items.find(item => item.id === action.payload)?.price * state.items.find(item => item.id === action.payload)?.quantity || 0),
            };
        
        case 'UPDATE_QUANTITY': {
            const item = state.items.find(item => item.id === action.payload.id);
            const difference = (action.payload.quantity - item.quantity) * item.price;
            
            return {
                ...state,
                items: state.items.map(item =>
                    item.id === action.payload.id
                        ? { ...item, quantity: action.payload.quantity }
                        : item
                ),
                total: state.total + difference,
            };
        }
        
        case 'CLEAR_CART':
            return initialState;
        
        default:
            return state;
    }
};

export const CartProvider = ({ children }) => {
    const [state, dispatch] = useReducer(cartReducer, initialState);

    const addItem = (id, name, price, quantity = 1) => {
        dispatch({
            type: 'ADD_ITEM',
            payload: { id, name, price, quantity },
        });
    };

    const removeItem = (id) => {
        dispatch({
            type: 'REMOVE_ITEM',
            payload: id,
        });
    };

    const updateQuantity = (id, quantity) => {
        if (quantity > 0) {
            dispatch({
                type: 'UPDATE_QUANTITY',
                payload: { id, quantity },
            });
        }
    };

    const clearCart = () => {
        dispatch({ type: 'CLEAR_CART' });
    };

    const value = {
        items: state.items,
        total: state.total,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
    };

    return (
        <CartContext.Provider value={value}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) {
        throw new Error('useCart must be used within CartProvider');
    }
    return context;
};