import React, { createContext, useContext, useReducer } from 'react';

export const CartContext = createContext();

const initialState = {
    items: [],
    totalPrice: 0,
};

const cartReducer = (state, action) => {
    switch (action.type) {
        case 'ADD_TO_CART': {
            const existingItem = state.items.find(item => item.id === action.payload.id);
            
            if (existingItem) {
                return {
                    ...state,
                    items: state.items.map(item =>
                        item.id === action.payload.id
                            ? { ...item, quantity: item.quantity + (action.payload.quantity || 1) }
                            : item
                    ),
                    totalPrice: state.totalPrice + action.payload.price * (action.payload.quantity || 1),
                };
            }
            
            return {
                ...state,
                items: [...state.items, { ...action.payload, quantity: action.payload.quantity || 1 }],
                totalPrice: state.totalPrice + action.payload.price * (action.payload.quantity || 1),
            };
        }

        case 'REMOVE_FROM_CART':
            const removedItem = state.items.find(item => item.id === action.payload);
            return {
                ...state,
                items: state.items.filter(item => item.id !== action.payload),
                totalPrice: state.totalPrice - (removedItem?.price * removedItem?.quantity || 0),
            };

        case 'UPDATE_QUANTITY':
            return {
                ...state,
                items: state.items.map(item =>
                    item.id === action.payload.id
                        ? { ...item, quantity: action.payload.quantity }
                        : item
                ),
                totalPrice: state.items.reduce((sum, item) => {
                    if (item.id === action.payload.id) {
                        return sum + action.payload.quantity * item.price;
                    }
                    return sum + item.quantity * item.price;
                }, 0),
            };

        case 'CLEAR_CART':
            return initialState;

        default:
            return state;
    }
};

export const CartProvider = ({ children }) => {
    const [state, dispatch] = useReducer(cartReducer, initialState);

    const addToCart = (id, name, price, quantity = 1) => {
        dispatch({ type: 'ADD_TO_CART', payload: { id, name, price, quantity } });
    };

    const removeFromCart = (id) => {
        dispatch({ type: 'REMOVE_FROM_CART', payload: id });
    };

    const updateQuantity = (id, quantity) => {
        if (quantity <= 0) {
            removeFromCart(id);
        } else {
            dispatch({ type: 'UPDATE_QUANTITY', payload: { id, quantity } });
        }
    };

    const clearCart = () => {
        dispatch({ type: 'CLEAR_CART' });
    };

    return (
        <CartContext.Provider value={{ ...state, addToCart, removeFromCart, updateQuantity, clearCart }}>
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