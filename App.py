import tkinter as tk
from Simplex import SimplexMethod

def convert_to_float(frac_str):
    """
    Chuyển đổi một chuỗi thành số thực.

    Parameters
    ----------
    frac_str : str
        Chuỗi chứa số phân số hoặc số thập phân.

    Returns
    -------
    float or None
        Giá trị số thực hoặc None nếu không thể chuyển đổi.
    """
    try:
        return float(frac_str)
    except ValueError:
        try:
            num, denom = frac_str.split('/')
        except ValueError:
            return None

        try:
            leading, num = num.split(' ')
        except ValueError:
            return float(num) / float(denom)

        if float(leading) < 0:
            sign_mult = -1
        else:
            sign_mult = 1

        return float(leading) + sign_mult * (float(num) / float(denom))


class LinearProgrammingApp:
    def __init__(self):
        """
        Khởi tạo một đối tượng LinearProgrammingApp.

        - Tạo một cửa sổ Tkinter.
        - Khởi tạo các biến IntVar để lưu trữ giá trị cho các thành phần giao diện.
        - Khởi tạo các danh sách để lưu trữ các thành phần giao diện.
        """
        self.window = tk.Tk()
        self.constraint_window = None
        self.window.title("Linear Programming")
        self.prob_var = tk.IntVar()
        self.n_vars_var = tk.IntVar()
        self.n_ub_constraints_var = tk.IntVar()
        self.n_lb_constraints_var = tk.IntVar()
        self.n_eq_constraints_var = tk.IntVar()

        self.ub_constraints_entries = []
        self.lb_constraints_entries = []
        self.eq_constraints_entries = []
        self.A_ub_constraints_entries = []
        self.b_ub_constraints_entries = []
        self.A_lb_constraints_entries = []
        self.b_lb_constraints_entries = []
        self.A_eq_constraints_entries = []
        self.b_eq_constraints_entries = []

        self.variable_bounds_entries = []
        self.c_entries = []

    def switch_to_constraints_page(self):
        """
        Chuyển sang trang ràng buộc trong ứng dụng.

        - Ẩn cửa sổ hiện tại.
        - Tạo cửa sổ cho việc nhập ràng buộc.
        """
        self.window.withdraw()
        self.create_constraints_input_window()


    def switch_to_result_page(self):
        """
        Chuyển sang trang kết quả trong ứng dụng.

        - Ẩn cửa sổ nhập ràng buộc hiện tại.
        - Nhận thông tin về ràng buộc từ đầu vào của người dùng.
        - Sử dụng phương pháp Simplex để giải bài toán tối ưu tuyến tính.
        - Hiển thị kết quả tối ưu lên giao diện.
        """
        self.constraint_window.withdraw()
        c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds = self.get_constrainst_from_user_input()
        # c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds = self.user_input_from_terminal()
        simplex = SimplexMethod(c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds, self.prob)
        x, fun, status = simplex.run_simplex()
        self.display_result(x, fun, status)


    def create_general_input_window(self):
        """
        Tạo cửa sổ nhập thông tin chung trong ứng dụng.

        - Tạo các nhãn và các nút radio để chọn Min hoặc Max.
        - Tạo các ô nhập liệu cho số biến, số ràng buộc <=, >=, =.
        - Tạo nút "Tiếp tục" để chuyển sang trang nhập ràng buộc.
        - Hiển thị cửa sổ và lắng nghe các sự kiện từ giao diện.
        """
        tk.Label(self.window, text="Min/Max:").pack()
        tk.Radiobutton(self.window, text="Min", variable=self.prob_var, value=1).pack()
        tk.Radiobutton(self.window, text="Max", variable=self.prob_var, value=0).pack()

        tk.Label(self.window, text="Số biến:").pack()
        tk.Entry(self.window, textvariable=self.n_vars_var).pack()

        tk.Label(self.window, text="Số ràng buộc <=:").pack()
        tk.Entry(self.window, textvariable=self.n_ub_constraints_var).pack()

        tk.Label(self.window, text="Số ràng buộc >=:").pack()
        tk.Entry(self.window, textvariable=self.n_lb_constraints_var).pack()

        tk.Label(self.window, text="Số ràng buộc =:").pack()
        tk.Entry(self.window, textvariable=self.n_eq_constraints_var).pack()

        tk.Button(self.window, text="Tiếp tục", command=self.switch_to_constraints_page).pack()

        self.window.mainloop()


    def create_constraints_input_window(self):
        """
        Tạo cửa sổ nhập thông tin về ràng buộc trong ứng dụng.

        - Lấy số lượng ràng buộc <=, >=, = và số biến từ người dùng.
        - Tạo cửa sổ con và đặt tiêu đề "Linear Programming - Ràng buộc".
        - Thiết lập sự kiện khi người dùng đóng cửa sổ con.
        - Tạo nhãn và ô nhập liệu cho hàm mục tiêu.
        - Tạo nhãn và ô nhập liệu cho các ràng buộc <=.
        - Tạo nhãn và ô nhập liệu cho các ràng buộc >=.
        - Tạo nhãn và ô nhập liệu cho các ràng buộc =.
        - Tạo nhãn và ô nhập liệu cho giới hạn biến.
        - Tạo nút "Tiếp tục" để chuyển sang trang kết quả.
        """
        self.n_ub_constraints = self.n_ub_constraints_var.get()
        self.n_lb_constraints = self.n_lb_constraints_var.get()
        self.n_eq_constraints = self.n_eq_constraints_var.get()
        self.n_vars = self.n_vars_var.get()
        self.constraint_window = tk.Toplevel()
        self.constraint_window.title("Linear Programming - Ràng buộc")
        self.constraint_window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.constraint_window.columnconfigure(index=1, weight=1)
        tk.Label(self.constraint_window, text="Hàm mục tiêu:").grid(row=0,columnspan=20)

        tk.Label(self.constraint_window, text="z = ").grid(row=1,column=0)
        for i in range(self.n_vars):
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=1,column=2*i+1)
            if i ==self.n_vars-1:
                tk.Label(self.constraint_window, text=f"x{i+1}").grid(row=1,column=2*i+2)
            else:
                tk.Label(self.constraint_window, text=f"x{i+1} +").grid(row=1,column=2*i+2)
            self.c_entries.append(entry)

        # Các ràng buộc <=
        for i in range(2,2+self.n_ub_constraints):
            entry_list=[]
            for j in range(self.n_vars):
                entry=tk.Entry(self.constraint_window)
                entry.grid(row=i,column=2*j) 
                if j == self.n_vars-1:
                    tk.Label(self.constraint_window,text=f"x{j+1}").grid(row=i,column=2*j+1)
                else:
                    tk.Label(self.constraint_window,text=f"x{j+1} +").grid(row=i,column=2*j+1)
                entry_list.append(entry)
            tk.Label(self.constraint_window,text="<=").grid(row=i,column=2*self.n_vars)
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=i,column=2*self.n_vars+1)
            entry_list.append(entry)
            self.ub_constraints_entries.append(entry_list)

        # Các ràng buộc >=
        for i in range(2+self.n_ub_constraints,2+self.n_ub_constraints+ self.n_lb_constraints):
            entry_list=[]
            for j in range(self.n_vars):
                entry=tk.Entry(self.constraint_window)
                entry.grid(row=i,column=2*j) 
                if j == self.n_vars-1:
                    tk.Label(self.constraint_window,text=f"x{j+1}").grid(row=i,column=2*j+1)
                else:
                    tk.Label(self.constraint_window,text=f"x{j+1} +").grid(row=i,column=2*j+1)
                entry_list.append(entry)
            tk.Label(self.constraint_window,text=">=").grid(row=i,column=2*self.n_vars)
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=i,column=2*self.n_vars+1)
            entry_list.append(entry)
            self.lb_constraints_entries.append(entry_list)

        # Các ràng buộc =
        for i in range(2+self.n_ub_constraints+self.n_lb_constraints,2+self.n_ub_constraints+self.n_lb_constraints+ self.n_eq_constraints):
            entry_list=[]
            for j in range(self.n_vars):
                entry=tk.Entry(self.constraint_window)
                entry.grid(row=i,column=2*j) 
                if j == self.n_vars-1:
                    tk.Label(self.constraint_window,text=f"x{j+1}").grid(row=i,column=2*j+1)
                else:
                    tk.Label(self.constraint_window,text=f"x{j+1} +").grid(row=i,column=2*j+1)
                entry_list.append(entry)
            self.A_eq_constraints_entries.append(entry_list)
            tk.Label(self.constraint_window,text="=").grid(row=i,column=2*self.n_vars)
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=i,column=2*self.n_vars+1)
            entry_list.append(entry)
            self.eq_constraints_entries.append(entry_list)

        # Giới hạn biến
        for i in range(2+self.n_ub_constraints+self.n_lb_constraints+self.n_eq_constraints,2+self.n_ub_constraints+self.n_lb_constraints+ self.n_eq_constraints +self.n_vars):
            bounds=[]
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=i,column=0)
            bounds.append(entry)
            tk.Label(self.constraint_window, text=f" <= x{i-(self.n_ub_constraints+self.n_lb_constraints+self.n_eq_constraints+1)} <= ").grid(row=i,column=1)
            entry=tk.Entry(self.constraint_window)
            entry.grid(row=i,column=2)
            bounds.append(entry)
            self.variable_bounds_entries.append(bounds)

        submit_button = tk.Button(self.constraint_window, text="Tiếp tục", command=self.switch_to_result_page)
        submit_button.grid(row=2+self.n_ub_constraints+self.n_lb_constraints+self.n_eq_constraints+self.n_vars+2,columns=10)

    def get_constrainst_from_user_input(self):
        # Lấy giá trị từ các biến và danh sách ràng buộc
        self.prob = self.prob_var.get()
        c = []
        A_ub = None
        b_ub = None
        A_lb = None
        b_lb = None
        A_eq = None
        b_eq = None

        # Lấy giá trị hàm mục tiêu
        for c_entry in self.c_entries:
            c.append(convert_to_float(c_entry.get().strip()))

        # Lấy giá trị và tạo danh sách ràng buộc <=
        if self.n_ub_constraints > 0:
            A_ub = []
            b_ub = []

        for constraint_entry in self.ub_constraints_entries:
            constraint = list(map(lambda x: convert_to_float(x), [i.get().strip() for i in constraint_entry]))
            A_ub.append(constraint[:-1])
            b_ub.append(constraint[-1])

        # Lấy giá trị và tạo danh sách ràng buộc >=
        if self.n_lb_constraints > 0:
            A_lb = []
            b_lb = []

        for constraint_entry in self.lb_constraints_entries:
            constraint = list(map(lambda x: convert_to_float(x), [i.get().strip() for i in constraint_entry]))
            # constraint = map(lambda x: convert_to_float(x), [i.get().strip() for i in constraint_entry])
            # constraint = list(map(lambda x: -x, constraint))
            A_lb.append(constraint[:-1])
            b_lb.append(constraint[-1])

        # Lấy giá trị và tạo danh sách ràng buộc =
        if self.n_eq_constraints > 0:
            A_eq = []
            b_eq = []

        for constraint_entry in self.eq_constraints_entries:
            constraint = list(map(lambda x: convert_to_float(x), [i.get().strip() for i in constraint_entry]))
            A_eq.append(constraint[:-1])
            b_eq.append(constraint[-1])

        # Lấy giá trị và tạo danh sách giới hạn biến
        bounds = []
        for variable_bounds in self.variable_bounds_entries:
            bound = [None] * 2
            for i, bound_entry in enumerate(variable_bounds):
                bound_value = bound_entry.get().strip()
                if bound_value == 'None':
                    continue
                bound[i] = convert_to_float(bound_value)
            bounds.append(bound)
        return c, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, bounds

    def display_result(self, x, fun, status):
        self.result_window = tk.Toplevel(self.window)
        self.result_window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        
        # Xử lý các trạng thái của bài toán tối ưu
        if status == 2:
            tk.Label(self.result_window, text="Bài toán vô nghiệm").pack()
            tk.Button(self.result_window, text="Kết thúc", command=self.window.destroy).pack()
            return
        if status == 3:
            if self.prob == 1:
                tk.Label(self.result_window, text="Giá trị tối ưu z = -oo").pack()
            else:
                tk.Label(self.result_window, text="Giá trị tối ưu z = +oo").pack()
            tk.Button(self.result_window, text="Kết thúc", command=self.window.destroy).pack()
            return
        
        # Hiển thị nghiệm và giá trị tối ưu
        tk.Label(self.result_window, text="Nghiệm của phương trình là ").pack()
        for i in range(self.n_vars_var.get()):
            tk.Label(self.result_window, text=f"x{i+1} : {x[i]}").pack()

        tk.Label(self.result_window, text="Giá trị tối ưu là ").pack()
        if self.prob == 1:
            tk.Label(self.result_window, text=f"Min z = {fun}").pack()
        else:
            tk.Label(self.result_window, text=f"Max z = {fun}").pack()
        
        tk.Button(self.result_window, text="Kết thúc", command=self.window.destroy).pack()

        
    # def _user_input_from_terminal(self):
    #     A_ub = None
    #     A_lb = None
    #     A_eq = None
    #     b_ub = None
    #     b_lb = None
    #     b_eq = None
    #     bounds = []
    #     prob = int(input('(Min : 1/ Max : 0) : '))
    #     n_vars = int(input('Nhap so bien : '))
    #     try:
    #         n_ub_constraints = int(input('Nhap so rang buoc <= : '))
    #     except ValueError as e:
    #         raise TypeError(
    #             "Invalid input for n_ub_constraints: n_ub_constraints must be natural number") from e
    #     else:
    #         if n_ub_constraints <0:
    #             raise ValueError('n_ub_constrants must be > 0')
        

    #     try:
    #         n_lb_constraints = int(input('Nhap so rang buoc >= : '))
    #     except ValueError as e:
    #         raise TypeError(
    #             "Invalid input for n_lb_constraints: n_lb_constraints must be natural number") from e
    #     else:
    #         if n_ub_constraints <0:
    #             raise ValueError('n_lb_constrants must be > 0')


    #     try:
    #         n_eq_constraints = int(input('Nhap so rang buoc = : '))
    #     except ValueError as e:
    #         raise TypeError(
    #             "Invalid input for n_eq_constraints: n_eq_constraints must be natural number") from e
    #     else:
    #         if n_ub_constraints <0:
    #             raise ValueError('n_eq_constrants must be > 0')
    #     c = map(lambda x : convert_to_float(x), input(
    #         'Nhap ham muc tieu :  \n Vi du : z= 2x1+3x2 thi nhap la "2 3" :\n').strip().split())
    #     if prob == 0:
    #         c = map(lambda x: -x, c)
    #     c = list(c)

    #     if n_ub_constraints > 0:
    #         A_ub = []
    #         b_ub = []
    #         print('Nhap rang buoc <= (theo tung dong): \nVi du : 2x1 + 3x2 <= 10 thi nhap la "2 3 10" :')
    #         while (n_ub_constraints > 0):
    #             ub_constraint = list(map(lambda x : convert_to_float(x), input().strip().split()))
    #             A_ub.append(ub_constraint[:-1])
    #             b_ub.append(ub_constraint[-1])
    #             n_ub_constraints -= 1
    #     if n_lb_constraints > 0:
    #         A_lb = []
    #         b_lb = []
    #         print('Nhap rang buoc >= (theo tung dong): \nVi du : 2x1 + 3x2 >= 10 thi nhap la "2 3 10" :')
    #         while (n_lb_constraints > 0):
    #             lb_constraint = list(map(lambda x : convert_to_float(x), input().strip().split()))
    #             A_lb.append(lb_constraint[:-1])
    #             b_lb.append(lb_constraint[-1])
    #             n_lb_constraints -= 1
    #     if n_eq_constraints > 0:
    #         A_eq = []
    #         b_eq = []
    #         print('Nhap rang buoc = (theo tung dong): \nVi du : 2x1 + 3x2 = 10 thi nhap la "2 3 10" :')
    #         while (n_eq_constraints > 0):
    #             eq_constraint = list(
    #                 map(lambda x : convert_to_float(x), input().strip().split()))
    #             A_eq.append(eq_constraint[:-1])
    #             b_eq.append(eq_constraint[-1])
    #             n_eq_constraints -= 1
        
    #     print('Nhap rang buoc bien: \nVi du : x>=0 thi nhap la "0 None", 2<=x<=5 thi nhap la "2 5", con neu x khong co rang buoc gi thi nhap la "None None" :')
    #     while (n_vars > 0):
    #         bound = list(input().strip().split())
    #         if bound[0] == 'None':
    #             bound[0] = None
    #         if bound[1] == 'None':
    #             bound[1] = None
    #         if bound[0] is not None: 
    #             bound[0] = convert_to_float(bound[0])
    #         if bound[1] is not None:
    #             bound[1] = convert_to_float(bound[1])
    #         bounds.append(bound)
    #         n_vars -= 1
    #     return c, A_ub, b_ub,A_lb,b_lb, A_eq, b_eq, bounds, prob

    def run(self):
        self.create_general_input_window()
