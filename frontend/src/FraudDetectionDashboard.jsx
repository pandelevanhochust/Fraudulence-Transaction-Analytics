import {
  CheckCircleOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  WarningOutlined
} from '@ant-design/icons';
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Input,
  Modal,
  Row,
  Space,
  Spin,
  Statistic,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const { Title, Text } = Typography;
const { TextArea } = Input;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const FraudDetectionDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newTransaction, setNewTransaction] = useState('{}');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const transactionsRes = await fetch(`${API_BASE_URL}/api/transactions?page=${page}&size=${pageSize}`);
      if (!transactionsRes.ok) {
        throw new Error(`HTTP error! status: ${transactionsRes.status}`);
      }
      const transactionsData = await transactionsRes.json();

      const summaryRes = await fetch(`${API_BASE_URL}/api/transactions/summary`);
      if (!summaryRes.ok) {
        throw new Error(`HTTP error! status: ${summaryRes.status}`);
      }
      const summaryData = await summaryRes.json();

      setTransactions(transactionsData.items || []);
      setTotalPages(transactionsData.pages || 1);
      setSummary(summaryData);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
      message.error(`Failed to load data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const addTransaction = async () => {
    try {
      const data = JSON.parse(newTransaction);
      const response = await fetch(`${API_BASE_URL}/api/transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      message.success('Transaction added successfully');
      setNewTransaction('{}');
      setIsModalVisible(false);
      fetchData();
    } catch (err) {
      message.error(`Error adding transaction: ${err.message}`);
    }
  };

  const deleteTransaction = async (transactionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      message.success('Transaction deleted successfully');
      fetchData();
    } catch (err) {
      message.error(`Error deleting transaction: ${err.message}`);
    }
  };

  const clearAllTransactions = async () => {
    Modal.confirm({
      title: 'Are you sure you want to clear all transactions?',
      content: 'This action cannot be undone.',
      okText: 'Yes, Clear All',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/transactions`, {
            method: 'DELETE',
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          message.success('All transactions cleared');
          fetchData();
        } catch (err) {
          message.error(`Error clearing transactions: ${err.message}`);
        }
      },
    });
  };

  useEffect(() => {
    fetchData();
  }, [page]);

  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchData, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, page]);

  const getHourlyData = () => {
    const hourlyCount = new Array(24).fill(0);
    transactions.forEach((transaction) => {
      const hour = new Date(transaction.received_at).getHours();
      hourlyCount[hour]++;
    });
    return hourlyCount.map((count, hour) => ({
      hour: `${hour}:00`,
      transactions: count,
    }));
  };

  const getFraudStats = () => {
    const fraudCount = transactions.filter(
      (t) => t.data?.prediction === 1 || t.data?.fraud_probability > 0.5
    ).length;
    const normalCount = transactions.length - fraudCount;
    return { fraudCount, normalCount };
  };

  const columns = [
    {
      title: 'Transaction ID',
      dataIndex: 'transaction_id',
      key: 'transaction_id',
      render: (text) => <Text code style={{ fontSize: '12px' }}>{text}</Text>,
    },
    {
      title: 'Received At',
      dataIndex: 'received_at',
      key: 'received_at',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: 'Amount',
      dataIndex: ['data', 'amount'],
      key: 'amount',
      render: (amount) => amount ? `$${amount.toFixed(2)}` : 'N/A',
    },
    {
      title: 'Fraud Status',
      key: 'fraud_status',
      render: (_, record) => {
        const isFraud = record.data?.prediction === 1 || record.data?.fraud_probability > 0.5;
        return (
          <Tag color={isFraud ? 'red' : 'green'} icon={isFraud ? <WarningOutlined /> : <CheckCircleOutlined />}>
            {isFraud ? 'Fraud' : 'Normal'}
          </Tag>
        );
      },
    },
    {
      title: 'Fraud Probability',
      key: 'fraud_probability',
      render: (_, record) => {
        const prob = record.data?.fraud_probability;
        if (prob === undefined) return 'N/A';
        const percentage = (prob * 100).toFixed(2);
        return (
          <Text style={{ color: prob > 0.5 ? '#ff4d4f' : '#52c41a' }}>
            {percentage}%
          </Text>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          danger
          icon={<DeleteOutlined />}
          size="small"
          onClick={() => deleteTransaction(record.transaction_id)}
        >
          Delete
        </Button>
      ),
    },
  ];

  const fraudStats = getFraudStats();

  if (loading && !transactions.length) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" tip="Loading transaction data..." />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5', padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              <DatabaseOutlined /> Fraud Detection Dashboard
            </Title>
          </Col>
          <Col>
            <Space>
              <Switch
                checked={autoRefresh}
                onChange={setAutoRefresh}
                checkedChildren="Auto-refresh ON"
                unCheckedChildren="Auto-refresh OFF"
              />
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalVisible(true)}
              >
                Add Transaction
              </Button>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={clearAllTransactions}
              >
                Clear All
              </Button>
              <Button
                icon={<ReloadOutlined spin={loading} />}
                onClick={fetchData}
                loading={loading}
              >
                Refresh
              </Button>
            </Space>
          </Col>
        </Row>

        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            closable
            style={{ marginBottom: '24px' }}
            onClose={() => setError(null)}
          />
        )}

        <Divider />

        {/* Summary Statistics */}
        {summary && (
          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Total Transactions"
                  value={summary.total_transactions}
                  prefix={<DatabaseOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Fraudulent"
                  value={fraudStats.fraudCount}
                  prefix={<WarningOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Normal"
                  value={fraudStats.normalCount}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Latest Transaction"
                  value={summary.latest_transaction ? new Date(summary.latest_transaction).toLocaleString() : 'None'}
                  prefix={<ReloadOutlined />}
                />
              </Card>
            </Col>
          </Row>
        )}

        {/* Hourly Chart */}
        {transactions.length > 0 && (
          <Card title="Hourly Transaction Pattern" style={{ marginBottom: '24px' }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getHourlyData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="transactions" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Transactions Table */}
        <Card title="Recent Transactions">
          <Table
            columns={columns}
            dataSource={transactions}
            rowKey="transaction_id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: summary?.total_transactions || 0,
              showTotal: (total) => `Total ${total} transactions`,
              onChange: (page) => setPage(page),
            }}
            expandable={{
              expandedRowRender: (record) => (
                <pre style={{ background: '#f5f5f5', padding: '16px', borderRadius: '4px' }}>
                  {JSON.stringify(record.data, null, 2)}
                </pre>
              ),
            }}
          />
        </Card>
      </Card>

      {/* Add Transaction Modal */}
      <Modal
        title="Add New Transaction"
        open={isModalVisible}
        onOk={addTransaction}
        onCancel={() => {
          setIsModalVisible(false);
          setNewTransaction('{}');
        }}
        okText="Add Transaction"
        cancelText="Cancel"
      >
        <TextArea
          rows={8}
          value={newTransaction}
          onChange={(e) => setNewTransaction(e.target.value)}
          placeholder='{"amount": 100, "user_id": "user123", "merchant_id": "merchant456", "timestamp": "2024-01-01T00:00:00"}'
        />
      </Modal>
    </div>
  );
};

export default FraudDetectionDashboard;
