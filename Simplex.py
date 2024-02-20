import numpy as np
from collections import namedtuple

class SimplexMethod:
    def __init__(self,c,A_ub=None,b_ub=None,A_lb=None,b_lb=None,A_eq=None,b_eq=None,bounds=None,prob=1) -> None:

        self._LPProblem = namedtuple('_LPProblem','c A_ub b_ub A_lb b_lb A_eq b_eq bounds prob')

        self.lp=self._LPProblem(c,A_ub,b_ub,A_lb,b_lb,A_eq,b_eq,bounds,prob)

    def _clean_inputs(self):
        c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds, prob = self.lp
        if c is None:
            raise ValueError
        n_x = len(c)
        c = np.array(c, dtype=np.float64, copy=True).squeeze()
        if c.size==1:
            c=c.reshape((-1))
        if A_ub is None:
            A_ub = np.zeros((0, n_x), dtype=float)
        else:
            A_ub = np.array(A_ub, dtype=float, copy=True)

        if b_ub is None:
            b_ub = np.array([], dtype=float)
        else:
            b_ub = np.array(b_ub, dtype=float, copy=True).squeeze()
            if b_ub.size == 1:
                b_ub = b_ub.reshape((-1))

        if A_lb is None:
            A_lb = np.zeros((0, n_x), dtype=float)
        else:
            A_lb = np.array(A_lb, dtype=float, copy=True)

        if b_lb is None:
            b_lb = np.array([], dtype=float)
        else:
            b_lb = np.array(b_lb, dtype=float, copy=True).squeeze()
            if b_lb.size == 1:
                b_lb = b_lb.reshape((-1))

        if A_eq is None:
            A_eq = np.zeros((0, n_x), dtype=float)
        else:
            A_eq = np.array(A_eq, dtype=float, copy=True)

        if b_eq is None:
            b_eq = np.array([], dtype=float)
        else:
            b_eq = np.array(b_eq, dtype=float, copy=True).squeeze()
            if b_eq.size == 1:
                b_eq = b_eq.reshape((-1))

        bounds_clean = np.array(bounds, dtype=float)

        # Quá trình trên tạo ra các giá trị nan khi đầu vào chỉ định None
        # Chuyển các giá trị nan trong cột thứ nhất thành -np.inf và trong cột thứ hai
        # thành np.inf
        i_none = np.isnan(bounds_clean[:, 0])
        bounds_clean[i_none, 0] = -np.inf
        i_none = np.isnan(bounds_clean[:, 1])
        bounds_clean[i_none, 1] = np.inf

        # Trả về _LPProblem(c, A_ub, b_ub, A_eq, b_eq, bounds_clean)
        self.lp = self._LPProblem(c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds_clean, prob)


    def _get_Abc(self,c0=0):
        c, A_ub, b_ub,A_lb,b_lb,A_eq, b_eq, bounds,prob = self.lp

        if prob == 0:
            c=-c
            self.lp=self._LPProblem(c,A_ub,b_ub,A_lb,b_lb,A_eq,b_eq,bounds,prob)
        A_ub = np.concatenate((A_ub,-A_lb))
        b_ub = np.concatenate((b_ub,-b_lb))
        
        bounds = np.array(bounds, copy=True)

        
        lbs = bounds[:, 0]
        ubs = bounds[:, 1]
        m_ub, n_ub = A_ub.shape

        lb_none = np.equal(lbs, -np.inf)
        ub_none = np.equal(ubs, np.inf)
        lb_some = np.logical_not(lb_none)
        ub_some = np.logical_not(ub_none)

        # Xử lý trường hợp không có cận dưới và có cận trên (biến đổi từ -inf <=xi<=ub sang -ub <= xi <= inf)
        l_nolb_someub = np.logical_and(lb_none, ub_some)
        i_nolb = np.nonzero(l_nolb_someub)[0]
        lbs[l_nolb_someub], ubs[l_nolb_someub] = (
            -ubs[l_nolb_someub], -lbs[l_nolb_someub])
        lb_none = np.equal(lbs, -np.inf)
        ub_none = np.equal(ubs, np.inf)
        lb_some = np.logical_not(lb_none)
        ub_some = np.logical_not(ub_none)
        c[i_nolb] *= -1

        if len(i_nolb) > 0:
            A_ub[:, i_nolb] *= -1
            A_eq[:, i_nolb] *= -1

        # Xử lý trường hợp có cận trên vào dưới
        # Tách lb <= xi <= ub thành một constraint là lb <= xi và thêm xi<=ub vào A_ub
        i_newub, = ub_some.nonzero()
        ub_newub = ubs[ub_some]
        n_bounds = len(i_newub)
        if n_bounds > 0:
            shape = (n_bounds, A_ub.shape[1])
            A_ub = np.vstack((A_ub, np.zeros(shape)))
            A_ub[np.arange(m_ub, A_ub.shape[0]), i_newub] = 1
            b_ub = np.concatenate((b_ub, np.zeros(n_bounds)))
            b_ub[m_ub:] = ub_newub

        A1 = np.vstack((A_ub, A_eq))
        b = np.concatenate((b_ub, b_eq))
        c = np.concatenate((c, np.zeros((A_ub.shape[0],))))

        # Xử lý trường hợp biến tự do
        # Thay biến tự do x thành x+ + x-
        l_free = np.logical_and(lb_none, ub_none)
        i_free = np.nonzero(l_free)[0]
        n_free = len(i_free)
        c = np.concatenate((c, np.zeros(n_free)))

        A1 = np.hstack((A1[:, :n_ub], -A1[:, i_free]))
        c[n_ub:n_ub+n_free] = -c[i_free]

        # Thêm các biến phụ để biến các constraint <= thành =
        A2 = np.vstack([np.eye(A_ub.shape[0]), np.zeros(
            (A_eq.shape[0], A_ub.shape[0]))])
        A = np.hstack([A1, A2])

        
        # Biến đổi các cận dưới thành 0
        # Thay xi bởi xi+lb 
        i_shift = np.nonzero(lb_some)[0]
        lb_shift = lbs[lb_some].astype(float)
        c0 += np.sum(lb_shift * c[i_shift])
        b -= (A[:, i_shift] * lb_shift).sum(axis=1)

        return A, b, c, c0

    # Tìm biến vào cơ sở
    def _pivot_col(self, T, tol=1e-9, bland=False):
        ma = np.ma.masked_where(T[-1, :-1] >= -tol, T[-1, :-1], copy=False)
        if ma.count() == 0:
            return False, np.nan

        if bland:
            return True, np.nonzero(np.logical_not(np.atleast_1d(ma.mask)))[0][0]
        return True, np.ma.nonzero(ma == ma.min())[0][0]


    # Tìm biến ra cơ sở
    def _pivot_row(self,T, basis, pivcol, phase, tol=1e-9, bland=False):
        if phase == 1:
            k = 2
        else:
            k = 1
        ma = np.ma.masked_where(T[:-k, pivcol] <= tol, T[:-k, pivcol], copy=False)
        if ma.count() == 0:
            return False, np.nan
        mb = np.ma.masked_where(T[:-k, pivcol] <= tol, T[:-k, -1], copy=False)
        q = mb / ma
        min_rows = np.ma.nonzero(q == q.min())[0]
        if bland:
            return True, min_rows[np.argmin(np.take(basis, min_rows))]
        return True, min_rows[0]


    def _apply_pivot(self,T, basis, pivrow, pivcol):

        basis[pivrow] = pivcol
        pivval = T[pivrow, pivcol]
        T[pivrow] = T[pivrow] / pivval
        for irow in range(T.shape[0]):
            if irow != pivrow:
                T[irow] = T[irow] - T[pivrow] * T[irow, pivcol]

    # Chạy thuật toán đơn hình
    def _solve_simplex(self,T, basis,
                    maxiter=1000, tol=1e-9, phase=2, bland=False, nit0=0,
                    ):
        nit = nit0
        status = 0
        complete = False
        if phase == 2:
            for pivrow in [row for row in range(basis.size)
                        if basis[row] > T.shape[1] - 2]:
                non_zero_row = [col for col in range(T.shape[1] - 1)
                                if abs(T[pivrow, col]) > tol]
                if len(non_zero_row) > 0:
                    pivcol = non_zero_row[0]
                    self._apply_pivot(T, basis, pivrow, pivcol)
                    nit += 1

        while not complete:
            # Tìm biến vào
            pivcol_found, pivcol = self._pivot_col(T, tol, bland)
            if not pivcol_found:
                pivcol = np.nan
                pivrow = np.nan
                status = 0
                complete = True
            else:
                # Tìm biến ra
                pivrow_found, pivrow = self._pivot_row(
                    T, basis, pivcol, phase, tol, bland)
                if not pivrow_found:
                    status = 3
                    complete = True

            if not complete:
                if nit >= maxiter:
                    # Quá số lần lặp cho phép
                    status = 1
                    complete = True
                else:
                    self._apply_pivot(T, basis, pivrow, pivcol)
                    nit += 1
        return nit, status


    # Xử lý các trường hợp đơn hình
    def _linprog_simplex(self,c, c0, A, b,
                        maxiter=1000, tol=1e-9, bland=False):
        
        # Khởi đầu với status = 0
        status = 0
        messages = {0: "Optimization terminated successfully.", # Thuật toán thành công, phương trình có ngiệm
                    1: "Iteration limit reached.", # Quá số lần lặp cho phép, có thể bị xoay vòng, sử dụng Bland
                    2: "Optimization failed. Unable to find a feasible solution", # Không tìm được nghiệm tối ưu
                    3: "Optimization failed. The problem appears to be unbounded.", # Bài toán không giới nội, min z = -00
                    }

        n, m = A.shape

        # Tất cả b phải >0
        is_negative_constraint = np.less(b, 0)
        A[is_negative_constraint] *= -1
        b[is_negative_constraint] *= -1

        
        av = np.arange(n) + m
        basis = av.copy()

        # Ma trận T như đã trình bày trong file báo cáo
        row_constraints = np.hstack((A, np.eye(n), b[:, np.newaxis]))
        row_objective = np.hstack((c, np.zeros(n), c0))
        row_pseudo_objective = -row_constraints.sum(axis=0)
        row_pseudo_objective[av] = 0
        T = np.vstack((row_constraints, row_objective, row_pseudo_objective))

        nit1, status = self._solve_simplex(T, basis,
                                    maxiter=maxiter, tol=tol, phase=1,
                                    bland=bland
                                    )
        # Trường hợp min w=0 ,nghĩa là pha 1 thành công
        if abs(T[-1, -1]) < tol:
            # Xóa w 
            T = T[:-1, :]
            # Xóa biến giả
            T = np.delete(T, av, 1)
        else:
            # Trường hợp min w > 0 , pha 1 không tìm được nghiệm tối ưu, bài toán vô nghiệm
            status = 2
            messages[status] = (
                "Phase 1 of the simplex method failed to find a feasible solution."
            )

        # Nếu pha 1 thành công thì thực hiện pha 2
        if status == 0:
            # Pha 2
            nit2, status = self._solve_simplex(T, basis,
                                        maxiter=maxiter, tol=tol, phase=2,
                                        bland=bland, nit0=nit1
                                        )
        solution = np.zeros(n + m)
        solution[basis[:n]] = T[:n, -1]
        x = solution[:m]

        return x, status, messages[status]

    # Từ nghiệm của bài toán dạng chính tắc, chuyển về nghiệm của bài toán gốc
    def _postsolve(self,x):
        c, _, _,_,_,_, _, bounds,prob = self.lp
        n_x = bounds.shape[0]
        n_unbounded = 0
        for i, bi in enumerate(bounds):
            lbi = bi[0]
            ubi = bi[1]
            if lbi == -np.inf and ubi == np.inf:
                n_unbounded += 1
                x[i] = x[i] - x[n_x + n_unbounded - 1]
            else:
                if lbi == -np.inf:
                    x[i] = ubi - x[i]
                else:
                    x[i] += lbi
        x = x[:n_x]
        fun = x.dot(c)

        # Nếu prob là 0 tức là bài toán tìm max, đảo ngược kết quả
        if prob == 0:
            fun=-fun

        return x, fun

    def run_simplex(self):
        self._clean_inputs()
        A, b, c, c0 = self._get_Abc()
        x,status,_=self._linprog_simplex(c,c0,A,b)
        if status == 1:
            x,status,_=self._linprog_simplex(c,c0,A,b,bland=True)
        x,fun=self._postsolve(x)
        return x, fun, status