"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { CreditCard, CheckCircle2 } from "lucide-react"
import { useState } from "react"
import Image from "next/image"

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  courseTitle: string
  price: number
}

export function PaymentModal({ isOpen, onClose, onSuccess, courseTitle, price }: PaymentModalProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false)

  const handlePayment = () => {
    setIsProcessing(true)
    // Simulate payment processing
    setTimeout(() => {
      setIsProcessing(false)
      setIsComplete(true)
      // Simulate a delay before closing the modal
      setTimeout(() => {
        onSuccess()
        onClose()
        setIsComplete(false)
      }, 2000)
    }, 2000)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="text-center text-xl">Complete Your Purchase</DialogTitle>
        </DialogHeader>
        <div className="mt-4">
          {isComplete ? (
            <div className="flex flex-col items-center justify-center py-6">
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center mb-4">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-green-600">Payment Successful!</h3>
              <p className="text-sm text-gray-500 text-center mt-2">You have successfully enrolled in the course.</p>
            </div>
          ) : (
            <>
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h3 className="font-medium mb-2">Order Summary</h3>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{courseTitle}</span>
                  <span className="font-semibold">{price.toLocaleString("vi-VN")}</span>
                </div>
              </div>

              <div className="space-y-4">
                <Button
                  className="w-full bg-primary hover:bg-primary/90"
                  onClick={handlePayment}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                      Processing...
                    </div>
                  ) : (
                    <>
                      <CreditCard className="mr-2 h-4 w-4" />
                      Pay {price.toLocaleString("vi-VN")}
                    </>
                  )}
                </Button>

                <p className="text-xs text-center text-gray-500">
                  By completing your purchase you agree to our Terms of Service
                </p>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

