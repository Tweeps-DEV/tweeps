'use client';

import React, { useState, useEffect } from 'react';
import { ChevronLeft, Trash2, Plus, Minus } from 'lucide-react';
import Link from 'next/link';

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await fetch('/api/cart');
        if (!response.ok) throw new Error('Failed to fetch cart');
        const data = await response.json();
        setCartItems(data.items || []);
      } catch (error) {
        console.error('Error fetching cart:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCart();
  }, []);

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1 || newQuantity > 99) return;

    try {
      const response = await fetch(`/api/cart/items/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity })
      });

      if (!response.ok) throw new Error('Failed to update quantity');

      setCartItems(prev => prev.map(item => 
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      ));
    } catch (error) {
      console.error('Error updating quantity:', error);
    }
  };

  const removeItem = async (itemId) => {
    try {
      const response = await fetch(`/api/cart/items/${itemId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to remove item');

      setCartItems(prev => prev.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Error removing item:', error);
    }
  };

  const calculateTotal = () => {
    const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = subtotal * 0.1; // 10% tax
    const deliveryFee = 1.50;
    return {
      subtotal,
      tax,
      deliveryFee,
      total: subtotal + tax + deliveryFee
    };
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
      </div>
    );
  }

  const totals = calculateTotal();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center">
            <Link href="/dashboard" className="p-2 rounded-lg hover:bg-gray-100">
              <ChevronLeft className="h-6 w-6 text-gray-600" />
            </Link>
            <h1 className="ml-4 text-lg font-semibold">My Order</h1>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-6">
        {cartItems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Your cart is empty</p>
            <Link href="/dashboard" className="mt-4 inline-block text-red-500 hover:text-red-600">
              Browse Menu
            </Link>
          </div>
        ) : (
          <>
            {/* Cart Items */}
            <div className="space-y-4 mb-8">
              {cartItems.map((item) => (
                <div key={item.id} className="bg-white p-4 rounded-lg shadow-sm flex items-center">
                  <img
                    src={item.image_url || '/api/placeholder/80/80'}
                    alt={item.name}
                    className="w-20 h-20 object-cover rounded-lg"
                  />
                  <div className="ml-4 flex-grow">
                    <h3 className="font-medium">{item.name}</h3>
                    <p className="text-red-500">$ {item.price.toFixed(2)}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => removeItem(item.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="p-1 rounded-full bg-gray-100 hover:bg-gray-200"
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <span className="w-8 text-center">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="p-1 rounded-full bg-gray-100 hover:bg-gray-200"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Order Summary */}
            <div className="bg-white rounded-lg shadow-sm p-4 space-y-4">
              <h2 className="font-semibold text-lg">Order Summary</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span>$ {totals.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span>$ {totals.tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Delivery Fee</span>
                  <span>$ {totals.deliveryFee.toFixed(2)}</span>
                </div>
                <div className="pt-2 border-t flex justify-between font-semibold">
                  <span>Total</span>
                  <span>$ {totals.total.toFixed(2)}</span>
                </div>
              </div>
              <button
                onClick={() => window.location.href = '/checkout'}
                className="w-full bg-red-500 text-white py-3 rounded-lg hover:bg-red-600 transition-colors"
              >
                Checkout
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default CartPage;
