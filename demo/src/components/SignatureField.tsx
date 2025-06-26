import React, { useState, useRef } from 'react';
interface SignatureFieldProps {
  onSignatureComplete: (signed: boolean) => void;
}
const SignatureField: React.FC<SignatureFieldProps> = ({
  onSignatureComplete
}) => {
  const [isSigning, setIsSigning] = useState(false);
  const [signature, setSignature] = useState<string | null>(null);
  const [typedSignature, setTypedSignature] = useState('');
  const [signatureMethod, setSignatureMethod] = useState<'draw' | 'type'>('draw');
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawing = useRef(false);
  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    isDrawing.current = true;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.beginPath();
      // Get position for mouse or touch event
      let clientX, clientY;
      if ('touches' in e) {
        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;
      } else {
        clientX = e.clientX;
        clientY = e.clientY;
      }
      const rect = canvas.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      ctx.moveTo(x, y);
    }
  };
  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      // Get position for mouse or touch event
      let clientX, clientY;
      if ('touches' in e) {
        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;
        // Prevent scrolling while drawing
        e.preventDefault();
      } else {
        clientX = e.clientX;
        clientY = e.clientY;
      }
      const rect = canvas.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.strokeStyle = '#000';
      ctx.lineTo(x, y);
      ctx.stroke();
    }
  };
  const endDrawing = () => {
    if (!canvasRef.current) return;
    isDrawing.current = false;
    // Save the signature
    if (canvasRef.current) {
      const dataUrl = canvasRef.current.toDataURL();
      setSignature(dataUrl);
      onSignatureComplete(true);
    }
  };
  const clearSignature = () => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      setSignature(null);
      onSignatureComplete(false);
    }
  };
  const handleTypedSignature = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTypedSignature(e.target.value);
    onSignatureComplete(e.target.value.trim().length > 0);
  };
  const saveTypedSignature = () => {
    if (typedSignature.trim()) {
      setSignature('typed');
      setIsSigning(false);
    }
  };
  return <div className="border border-gray-200 rounded-md p-4">
      {!isSigning && !signature ? <div className="text-center">
          <p className="text-sm text-gray-500 mb-3">
            Please add your signature to continue
          </p>
          <button onClick={() => {
        setIsSigning(true);
        setSignatureMethod('draw');
      }} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
            Add Signature
          </button>
        </div> : isSigning ? <div>
          <div className="flex justify-center space-x-4 mb-4">
            <button className={`px-3 py-1 text-sm font-medium rounded-md ${signatureMethod === 'draw' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`} onClick={() => setSignatureMethod('draw')}>
              Draw
            </button>
            <button className={`px-3 py-1 text-sm font-medium rounded-md ${signatureMethod === 'type' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`} onClick={() => setSignatureMethod('type')}>
              Type
            </button>
          </div>
          {signatureMethod === 'draw' ? <div className="border border-gray-300 rounded-md bg-white">
              <canvas ref={canvasRef} width={400} height={150} className="w-full touch-none" onMouseDown={startDrawing} onMouseMove={draw} onMouseUp={endDrawing} onMouseLeave={endDrawing} onTouchStart={startDrawing} onTouchMove={draw} onTouchEnd={endDrawing} />
            </div> : <div>
              <input type="text" value={typedSignature} onChange={handleTypedSignature} placeholder="Type your signature" className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
              <div className="mt-2 p-3 border border-gray-200 rounded-md bg-white min-h-[80px] flex items-center justify-center">
                <span className="font-signature text-xl">{typedSignature}</span>
              </div>
            </div>}
          <div className="mt-4 flex justify-between">
            <button onClick={() => {
          setIsSigning(false);
          setSignature(null);
          if (signatureMethod === 'draw') {
            clearSignature();
          } else {
            setTypedSignature('');
          }
          onSignatureComplete(false);
        }} className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              Cancel
            </button>
            <div className="space-x-2">
              {signatureMethod === 'draw' && <button onClick={clearSignature} className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Clear
                </button>}
              <button onClick={signatureMethod === 'draw' ? () => setIsSigning(false) : saveTypedSignature} className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700" disabled={signatureMethod === 'type' && typedSignature.trim() === ''}>
                Save Signature
              </button>
            </div>
          </div>
        </div> : <div className="flex justify-between items-center">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="ml-2 text-sm text-gray-700">Signature added</span>
          </div>
          <button onClick={() => {
        setIsSigning(true);
        if (signatureMethod === 'draw') {
          clearSignature();
        }
      }} className="text-sm text-blue-600 hover:text-blue-500">
            Change
          </button>
        </div>}
    </div>;
};
export default SignatureField;