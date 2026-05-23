import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { ToastProvider } from "./components/Toast"
import ScrollToTop    from "./components/ScrollToTop"
import Navbar         from "./components/Navbar"
import Home           from "./pages/Home"
import Login          from "./pages/Login"
import Register       from "./pages/Register"
import Products       from "./pages/Products"
import ProductDetails from "./pages/ProductDetails"
import Cart           from "./pages/Cart"
import Orders         from "./pages/Orders"
import OrderDetail    from "./pages/OrderDetail"
import VendorDashboard from "./pages/VendorDashboard"
import ApiDocs        from "./pages/ApiDocs"
import Profile        from "./pages/Profile"
import NotFound       from "./pages/NotFound"
import AdminDashboard from "./pages/AdminDashboard"
import VendorPending  from "./pages/VendorPending"

function PrivateRoute({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" replace />
}

function VendorRoute({ children }) {
  const token = localStorage.getItem("token")
  const role  = localStorage.getItem("role")
  if (!token) return <Navigate to="/login" replace />
  if (role !== "vendor") return <Navigate to="/" replace />
  return children
}

function AdminRoute({ children }) {
  const token = localStorage.getItem("token")
  const role  = localStorage.getItem("role")
  if (!token) return <Navigate to="/login" replace />
  if (role !== "admin") return <Navigate to="/" replace />
  return children
}

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Navbar />
        <ScrollToTop />
        <Routes>
          <Route path="/"                 element={<Home />} />
          <Route path="/login"            element={<Login />} />
          <Route path="/register"         element={<Register />} />
          <Route path="/register-pending"  element={<VendorPending />} />
          <Route path="/products"         element={<Products />} />
          <Route path="/product/:id"      element={<ProductDetails />} />
          <Route path="/cart"             element={<PrivateRoute><Cart /></PrivateRoute>} />
          <Route path="/orders"           element={<PrivateRoute><Orders /></PrivateRoute>} />
          <Route path="/order-detail/:id" element={<PrivateRoute><OrderDetail /></PrivateRoute>} />
          <Route path="/vendor"           element={<VendorRoute><VendorDashboard /></VendorRoute>} />
          <Route path="/admin"            element={<AdminRoute><AdminDashboard /></AdminRoute>} />
          <Route path="/api-docs"         element={<ApiDocs />} />
          <Route path="/profile"          element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="*"                  element={<NotFound />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
